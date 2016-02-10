#!/usr/bin/env python

"""
Tab Extension for Markdown

* Markdown Example: 2 Tabs



```python

print('Hello World!')

```
```javascript

    document.writeln('Hello Word!');

```
```java

public class HelloWorld {

    public static void main(String[] args) {
        // Prints "Hello, World" to the terminal window.
        System.out.println("Hello, World");
    }

}

Above (Markdown)
*
|
|
|  Converts to
----------------|
                |
                |
                *
                Below (HTML)
```

<div>

    <!-- Nav tabs -->
    <ul class="nav nav-tabs" role="tablist">
        <li role="presentation" class="active"><a href="#python-tab" aria-controls="python" role="tab" data-toggle="tab">Python</a></li>
        <li role="presentation"><a href="#javascript-tab" aria-controls="javascript-tab" role="tab" data-toggle="tab">Javascript</a></li>
        <li role="presentation"><a href="#java-tab" aria-controls="java-tab" role="tab" data-toggle="tab">Java</a></li>
    </ul>

    <!-- Tab panes -->
    <div class="tab-content">
        ```python

        print('Hello World!')

        ```
    </div>

    <div class="tab-content">
        ```javascript

            document.writeln('Hello Word!');

        ```
    </div>

    <div class="tab-content">
        ```java

        public class HelloWorld {

            public static void main(String[] args) {
                // Prints "Hello, World" to the terminal window.
                System.out.println("Hello, World");
            }

        }
        ```
    </div>


</div>
"""
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from collections import deque
from time import time

import re
import random


class BSCodeTabSet(object):

    TAB_SET_HANDLE_CONTAINER_TEMPLATE = """
        <ul class="nav nav-tabs" role="tablist">
            {tabHandles}
        </ul>
    """
    TAB_SET_HANDLE_TEMPLATE = """
        <li role="presentation" class="{isTabActiveClass}">
            <a href="#{id}" aria-controls="{id}" role="tab" data-toggle="tab">{ulang}</a>
        </li>
    """
    TAB_SET_TAB_CONTAINER_TEMPLATE = """
        <div class="tab-content">
            {tabs}
        </div>
    """
    TAB_BODY_CONTAINER_TEMPLATE = """
        <div role="tabpanel" class="tab-pane {isTabActiveClass} fade in" id="{id}">
            {tabContent}
        </div>
    """
    RANDOM_ID_CHAR_LENGTH = 15


    def __init__(self, id):
        self.id = id
        self.codeTabs = deque()


    def add_code_tab(self, code_tab):
        self.codeTabs.append(code_tab)


    def get_code_tabs(self):
        return self.codeTabs


    def _get_tab_id(self, tab):

        tab_lang = tab.get_lang()
        tab_id = tab_lang

        if tab_lang is None or not tab_lang.strip():
            # http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python/23728630#23728630
            tab_id = ''. join(
                random.SystemRandom().choice(
                    string.ascii_lowercase + string.digits
                ) for _ in range(self.RANDOM_ID_CHAR_LENGTH)
            )

        tab_set_id = self.id + tab_id

        return tab_set_id


    def __str__(self):
        tab_active_class = 'active'
        tab_handles = ''
        tabs = ''

        for tab in self.codeTabs:

            tab_set_id = self._get_tab_id(tab)
            lang = tab.get_lang()

            tab_handles += self.TAB_SET_HANDLE_TEMPLATE.format(id = tab_set_id,
                                                               isTabActiveClass = tab_active_class,
                                                               lang = lang,
                                                               ulang = lang[0:1].capitalize() + lang[1:])

            tabs += self.TAB_BODY_CONTAINER_TEMPLATE.format(id = tab_set_id,
                                                            isTabActiveClass = tab_active_class,
                                                            lang = tab.get_lang(),
                                                            tabContent = str(tab))
            tab_active_class = ''

        tab_set_str = self.TAB_SET_HANDLE_CONTAINER_TEMPLATE.format(tabHandles = tab_handles)
        tab_set_str += self.TAB_SET_TAB_CONTAINER_TEMPLATE.format(tabs = tabs)

        return """
                <div>
                    {tabSet}
                </div>
                    """.format(tabSet = tab_set_str)


    def __repr__(self):
        return self.__str__()


class BSCodeTab(object):

    CODE_TAB_BODY_WRAP = """
            <pre><code{lang}>{code}</code></pre>
    """
    LANG_TAG = ' class="{lang}"'
    DEFAULT_LANG = 'source'


    def __init__(self, name, lang, body):
        self.name = name
        self.lang = lang.lower() if lang is not None else self.DEFAULT_LANG
        self.tabBody = body


    # Defaults to return a hilite style html block
    def __str__(self):
        return self.CODE_TAB_BODY_WRAP.format(
            lang = self.LANG_TAG.format(lang = self.lang.lower()),
            code = BSCodeTab.escape(self.tabBody)
        )

    def get_lang(self):
        return self.lang


    def __repr__(self):
        return self.__str__()

    @staticmethod
    def escape(txt):
        # HTML-entity-ize common characters
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


class CodeFencePreprocessor(Preprocessor):

    # FENCE_BLOCK_REGEX from https://github.com/amfarrell/fenced-code-plus
    FENCE_BLOCK_REGEX = re.compile(
        r'''(?xsm)
        (?P<fence>^(?:~{3,}|`{3,}))[ ]*                          # Opening
        (\{?\.?(?P<lang>[a-zA-Z0-9_+-]*))?[ ]*                   # Optional {, and lang
        (hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?[ ]*  # Optional highlight lines option
        }?[ ]*\n                                                 # Optional closing }
        (?P<code>.*?)(?<=\n)                                     # Code
        (?P=fence)[ ]*$                                          # Closing
        ''', re.MULTILINE | re.DOTALL | re.VERBOSE
    )
    CODE_TAB_PLACE_HOLDER_TEMPLATE = '<!-- {0}__code_tab__{{0}} -->'
    CODE_TAB_PLACE_HOLDER_REGEX_TEMPLATE = '<!-- {0}__code_tab__([0-9]+) -->'


    def __init__(self, md, code_fence_config = None):
        # Initialize the Preprocessor
        self.bs_tabs = deque()

        placeholder_dict = self._generate_tab_placeholder()
        self.tab_placeholder = placeholder_dict['placeholder']
        self.tab_placeholder_regex = placeholder_dict['placeholder_regex']

        self.code_fence_config = code_fence_config

        super(CodeFencePreprocessor, self).__init__(md)


    def _generate_tab_placeholder(self):

        # used to create a unique signature
        current_time = time()

        return {
            'placeholder': self.CODE_TAB_PLACE_HOLDER_TEMPLATE.format(current_time),
            'placeholder_regex': re.compile(self.CODE_TAB_PLACE_HOLDER_REGEX_TEMPLATE.format(current_time))
        }


    def _populate_tabs(self, parsed_placeholder_text):

        lines = parsed_placeholder_text.split('\n')
        start_tab_index = None
        tab_run_length = 0
        tab_set_count = 0
        transformed_lines = ''
        num_tabs = len(self.bs_tabs)
        show_all_code_as_folders = self.code_fence_config['show_all_code_as_folders']

        for line in lines:
            m = self.tab_placeholder_regex.search(line)

            if m:

                if start_tab_index is None:
                    start_tab_index = m.group(1)

                tab_run_length += 1

                # Ignore the remainder of the loop
                continue
            else:

                # We have a non tab save to the tab set so let's aggregate
                # the tabs into a tab set and generate the corresponding HTML
                if len(line.strip()) != 0 and start_tab_index is not None:

                    if show_all_code_as_folders or (not show_all_code_as_folders and tab_run_length > 1):
                        tab_set = BSCodeTabSet('tab-' + str(tab_set_count) + '-')
                        tab_set_count += 1

                        for i in range(0, tab_run_length):
                            tab = self.bs_tabs.popleft()
                            tab_set.add_code_tab(tab)

                        # Convert our tab set (and tabs) into the appropriate HTML
                        tab_html = str(tab_set)
                    else:
                        # Convert our single tab into the appropriate HTML
                        tab_html = str(self.bs_tabs.popleft())

                    start_tab_index = None
                    tab_run_length = 0
                    transformed_lines += '\n' + self.markdown.htmlStash.store(tab_html, safe = True) + '\n'

            # Put the newline back in the string
            transformed_lines += line + '\n'

        # If there are any remaining tabs enclose them in a final last tab set
        if len(self.bs_tabs) > 0:
            tab_set = BSCodeTabSet('tab-' + str(num_tabs) + '-')

            for tab in self.bs_tabs:
                tab_set.add_code_tab(tab)

            transformed_lines += '\n\n' + self.markdown.htmlStash.store(str(tab_set), safe = True) + '\n\n'
            self.bs_tabs.clear()

        # print(transformed_lines)
        return transformed_lines


    @staticmethod
    def filter_content(content):

        string_block = content.replace(u'\u2018', '&lsquo;')
        string_block = string_block.replace(u'\u2019', '&rsquo;')
        string_block = string_block.replace(u'\u201c', '&ldquo;')
        string_block = string_block.replace(u'\u201d', '&rdquo;')
        string_block = string_block.replace(u'\u2013', '&ndash;')
        string_block = string_block.replace(u'\xa0', '')

        try:
            string_block = string_block.decode('ascii', 'remove')
        except:
            string_block = content

        return string_block


    def _identify_code_tabs(self, block_str):

        string_block = CodeFencePreprocessor.filter_content(block_str)

        while True:

            m = self.FENCE_BLOCK_REGEX.search(string_block)

            if m:
                lang = self.code_fence_config['default_lang']

                if m.group('lang'):
                    lang = m.group('lang')

                # Add our tabs to our list.
                # We will later use this list to perform our aggregation into tab sets
                self.bs_tabs.append(BSCodeTab(lang, lang, m.group('code')))
                key = self.tab_placeholder.format(len(self.bs_tabs) - 1)

                # Replace the code fences with a tab placeholder
                string_block = '{0}\n{1}\n{2}'.format(
                    string_block[:m.start()],
                    key,
                    string_block[m.end():]
                )
            else:
                break

        # print(block_str)
        return string_block


    def run(self, lines):

        parsed_block_text = self._identify_code_tabs('\n'.join(lines))

        return self._populate_tabs(parsed_block_text).split('\n')


# Extension Class
class BSCodeTabExtension(Extension):

    def __init__(self, *args, **kwargs):

        # Config defaults
        self.config = {
            'default_lang': ['source', 'Sets the default language to be used when none is given in the ``` code block'],
            'show_all_code_as_folders': [True, 'Render all ``` code blocks as folders (even if there is only one)']
        }

        super(BSCodeTabExtension, self).__init__(*args, **kwargs)


    def extendMarkdown(self, md, md_globals):
        show_all_code_as_folders = self.getConfig('show_all_code_as_folders')

        # Just in case convert this parameter to a bool if it is sent in as a string
        if isinstance(show_all_code_as_folders, str):
            self.setConfig('show_all_code_as_folders', False if show_all_code_as_folders.upper() is 'FALSE' else True)

        md.registerExtension(self)

        # Add CodeFencePreprocessor to the Markdown instance.
        md.preprocessors.add('fenced_code_block',
                             CodeFencePreprocessor(md, self.getConfigs()),
                             '>normalize_whitespace')


def makeExtension(*args, **kwargs):
    return BSCodeTabExtension(*args, **kwargs)
