from runpype import Pype, Context


pype = Pype("Pipeline name")


# Add tasks

# The task keys on which this task depends
# are passed to the `require` parameter.


@pype.add_task(key="1", name="First argument")
def one(_: Context):
    return 1


@pype.add_task(key="2", name="Second argument", require={"1"})
def two(ctx: Context):
    return {"value": ctx.get("1") + 2}


@pype.add_task(key="3", name="Third argument", require={"2"})
def three(ctx: Context):
    return ctx.get("2")["value"] + 3


@pype.add_task(key="4", name="Fourth argument", require={"2"})
def four(ctx: Context):
    return ctx.get("2")["value"] + 4


@pype.add_task(key="5", name="Fifth argument", require={"1", "3"})
def five(ctx: Context):
    return ctx.get("1") + ctx.get("3")


# Run pipeline
pype.run()

# View result
print(repr(pype))

# Change some value
pype["1"] = 2

# View result after change
print(repr(pype))
