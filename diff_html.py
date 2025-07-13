#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import difflib
import os


def read_file_lines(path):
    if not os.path.exists(path):
        return ["[File not found: {}]\n".format(path)]
    with open(path, "r") as f:
        return f.readlines()


def generate_html_diff(before_path, after_path, label):
    before_lines = read_file_lines(before_path)
    after_lines = read_file_lines(after_path)

    differ = difflib.HtmlDiff()
    html_table = differ.make_table(
        before_lines,
        after_lines,
        fromdesc=f"Before - {label}",
        todesc=f"After - {label}",
        context=True,
        numlines=5
    )
    return html_table


def main():
    module_args = dict(
        before_file=dict(type='str', required=True),
        after_file=dict(type='str', required=True),
        label=dict(type='str', required=True),
        output_file=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    before_file = module.params['before_file']
    after_file = module.params['after_file']
    label = module.params['label']
    output_file = module.params['output_file']

    try:
        html_diff = generate_html_diff(before_file, after_file, label)

        with open(output_file, 'w') as f:
            f.write(f"""
            <html>
            <head>
              <style>
                body {{ font-family: monospace; }}
                table.diff {{ font-size: 12px; border: 1px solid #ccc; border-collapse: collapse; width: 100%; }}
                .diff_header {{ background-color: #f0f0f0; text-align: center; font-weight: bold; }}
                td.diff_header {{ background-color: #f0f0f0; }}
                .diff_next {{ background-color: #c0c0c0; }}
                .diff_add {{ background-color: #aaffaa; }}
                .diff_chg {{ background-color: #ffff77; }}
                .diff_sub {{ background-color: #ffaaaa; }}
                td {{ vertical-align: top; padding: 2px 5px; }}
              </style>
            </head>
            <body>
              <h2>Diff for Command: {label}</h2>
              {html_diff}
            </body>
            </html>
            """)

        module.exit_json(changed=True, diff_created=True, output_file=output_file)

    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
