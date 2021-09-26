import textwrap as tw
CODE = tw.dedent("""
    import os
    # print(a)
""",)

if __name__ == "__main__":
    a = 10
    globals = dict()
    exec(CODE, globals)
    print(globals)
    print(os.cpu_count())
