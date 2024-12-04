from runpype import Pype, Context


def one(_: Context):
    return 1


def two(ctx: Context):
    return ctx.get("1") + 2


def three(ctx: Context):
    return ctx.get("2") + 3


def four(ctx: Context):
    return ctx.get("2") + 4


def five(ctx: Context):
    return ctx.get("1") + ctx.get("3")


def main() -> None:
    # Create pipeline
    pype = Pype("Pipeline name")

    # Add tasks

    # The task keys on which this task depends
    # are passed to the `require` parameter.
    pype.add("1", "First argument", one)
    pype.add("2", "Second argument", two, require={"1"})
    pype.add("3", "Third argument", three, require={"2"})
    pype.add("4", "Fourth argument", four, require={"2"})
    pype.add("5", "Fifth argument", five, require={"1", "3"})

    # Run pipeline
    pype.run()

    # View result
    print(repr(pype))

    # Change some value
    pype["1"] = 2

    # View result after change
    print(repr(pype))


if __name__ == "__main__":
    main()
