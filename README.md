# 🚀 Runpype

A lightweight reactive task engine that allows you to connect task execution in a pipelines.

## There's no

- 🔥 Optimizations
- 🔁 Multi-threading
- 👽 External dependencies
- 🔬 Complicated code
- 🐳 Docker
- 🤖 CI/CD
- 🪲 Bugs (*but who knows*)

Just fun!

## 🗂️ Project structure

### 📁 `runpype/`

- **runpype.py**: All the code is here.
- `__init__.py`: Indicates that the folder is a Python module.

### 📂 Root files

- **LICENSE**: License.
- **README.md**: Project documentation.

### 📁 [`examples/`](/examples)

- Examples of Usage.

---

## 🛠️ Setup and startup

#### 1️⃣ Copy the `runpype/` folder to your project

Or just the `runpype.py` file from it.

#### 2️⃣ Import it in code

```python
from runpype import Pype
```

## Usage

```python
from runpype import Pype, Context

pype = Pype()

@pype.add_task(key="1", name="First func")
def one(_: Context):
    return 1

@pype.add_task(key="2", name="Second func", require={"1"})
def two(ctx: Context):
    return ctx.get("1") + 2

pype.run()

print(repr(pype))

pype["1"] = 2

print(repr(pype))
```

Result:

```bash
{
    "1": 1,
    "2": 3
}
{
    "1": 2,
    "2": 4
}
```
