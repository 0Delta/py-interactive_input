# Interactive input

## Useage


### install package

Install by `pip`

```
pip install interactive_input
```

### Cording

1. Import and instantiate.
1. regist keys,messages,hook functions
1. Call `Ask()`, it return key-value pair with value by user input.
1. If call `Ask()` more than once, object save previous input. so it can request only the increased.
1. You can overwrite value data with `overwrite=True` option.

```python
import interactive_input as iin

def main():
    var iinObj = iin.Object()
    iinObj.AddQ("key1")
    iinObj.AddQ("key2", message="Please Input", hook=base64enc)

    # this will delete value of "key1". (not delete key)
    iinObj.AddQ("key1", message="Overwrited", overwrite=True)

def base64enc(v: str) -> str:
    # you can something for user input. (e.g. hashing, encoding)
    return "encoded: " + v
```

### Run and Using

`Ask()` will present input UI like below.

```
Overwrited
Key1: _
Please Input
Key2: 
```

Can move allow-key or `jkl`.
`h` function as [BACKSPACE]. (can use BS normally as well)
[ENTER] can move next value. If hit [ENTER] with last line, Decide values and go next step.


### Bug

* Can't use non ascii character. it will broken data.
* Long input is not considered. When the sum of key and value lengths exceeds the console length, this program will clash.


## LICENCE

MIT

