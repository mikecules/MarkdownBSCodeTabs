from BSCodeTabExtension import BSCodeTabExtension
import markdown


simple_markdown_case = """```python
def foo2():
    bar = 16
    return 64
```

```javascript
alert('Hello World')
```"""


average_markdown_case = """
# Header 1

```python
def foo():
    bar = 4
    return 8
```

## Header 2

sdfdsf sd
f df
ds
f d


```python
def foo2():
    bar = 16
    return 64
```

```javascript
if (a > b) {
    alert('Hello World');
}
```

```sass
@import 'blah'
```


```
@import 'blah'
```

df sdf sdf
dsfd s
fds ds
f dsfds
 fs
  fsd
  dsfdsfsd


```perl
echo ('Hello World')
```

## Some sub header

dsfsdfdfdf sd fdfds
fds ds fdsfds fsdfs

```sql
  SELECT * FRO...
```
"""

print('\nSimple Markdown\n' + simple_markdown_case + '\n\nTranslates to...\n\n',
      markdown.markdown(simple_markdown_case, extensions=[BSCodeTabExtension()]))


print('\nAverage Markdown\n' + average_markdown_case + '\n\nTranslates to...\n\n',
      markdown.markdown(average_markdown_case, extensions=[BSCodeTabExtension()]))






