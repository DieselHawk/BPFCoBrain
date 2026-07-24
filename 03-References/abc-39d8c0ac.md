---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_vendor\rich\abc.py
imported: 2026-07-24T11:13:37.360176
file_type: .py
---

# abc.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_vendor\rich\abc.py`

## Content

```py
from abc import ABC


class RichRenderable(ABC):
    """An abstract base class for Rich renderables.

    Note that there is no need to extend this class, the intended use is to check if an
    object supports the Rich renderable protocol. For example::

        if isinstance(my_object, RichRenderable):
            console.print(my_object)

    """

    @classmethod
    def __subclasshook__(cls, other: type) -> bool:
        """Check if this class supports the rich render protocol."""
        return hasattr(other, "__rich_console__") or hasattr(other, "__rich__")


if __name__ == "__main__":  # pragma: no cover
    from pip._vendor.rich.text import Text

    t = Text()
    print(isinstance(Text, RichRenderable))
    print(isinstance(t, RichRenderable))

    class Foo:
        pass

    f = Foo()
    print(isinstance(f, RichRenderable))
    print(isinstance("", RichRenderable))

```
