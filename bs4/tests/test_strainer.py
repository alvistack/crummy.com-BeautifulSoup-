import pytest
import re
import warnings

from . import (
    SoupTest,
)
from bs4.element import Tag
from bs4.strainer import (
    AttributeValueMatchRule,
    MatchRule,
    SoupStrainer,
    StringMatchRule,
    TagNameMatchRule,
)

class TestMatchrule(SoupTest):

    def _tuple(self, rule):
        if isinstance(rule.pattern, str):
            import pdb; pdb.set_trace()

        return (
            rule.string,
            rule.pattern.pattern if rule.pattern else None,
            rule.function,
            rule.present
        )

    def tag_function(x:Tag) -> bool:
        return False

    def string_function(x:str) -> bool:
        return False

    @pytest.mark.parametrize(
        "constructor_args, constructor_kwargs, result",
        [
            # String
            ([], dict(string="a"), ("a", None, None, None)),
            ([], dict(string="\N{SNOWMAN}".encode("utf8")),
             ("\N{SNOWMAN}", None, None, None)),

            # Regular expression
            ([], dict(pattern=re.compile("a")), (None, "a", None, None)),
            ([], dict(pattern="b"), (None, "b", None, None)),
            ([], dict(pattern=b"c"), (None, "c", None, None)),

            # Function
            ([], dict(function=tag_function), (None, None, tag_function, None)),
            ([], dict(function=string_function), (None, None, string_function, None)),

            # Boolean
            ([], dict(present=True), (None, None, None, True)),

            # With positional arguments rather than keywords
            (("a", None, None, None), {}, ("a", None, None, None)),
            ((None, "b", None, None), {}, (None, "b", None, None)),
            ((None, None, tag_function, None), {},
             (None, None, tag_function, None)),
            ((None, None, None, True), {}, (None, None, None, True)),
        ]
    )
    def test_constructor(self, constructor_args, constructor_kwargs, result):
        rule = MatchRule(*constructor_args, **constructor_kwargs)
        assert result == self._tuple(rule)

    def test_empty_match_not_allowed(self):
        with pytest.raises(
                ValueError,
                match="Either string, pattern, function or present must be provided."
        ):
            MatchRule()

    def test_full_match_not_allowed(self):
        with pytest.raises(
                ValueError,
                match="At most one of string, pattern, function and present must be provided."
        ):
            MatchRule("a", "b", self.tag_function, True)

    @pytest.mark.parametrize(
        "rule_kwargs, match_against, result",
        [
            (dict(string="a"), "a", True),
            (dict(string="a"), "ab", False),

            (dict(pattern="a"), "a", True),
            (dict(pattern="a"), "ab", True),
            (dict(pattern="^a$"), "a", True),
            (dict(pattern="^a$"), "ab", False),

            (dict(present=True), "any random value", True),
            (dict(present=True), None, False),
            (dict(present=False), "any random value", False),
            (dict(present=False), None, True),

            (dict(function=lambda x: x.upper() == x), "UPPERCASE", True),
            (dict(function=lambda x: x.upper() == x), "lowercase", False),

            (dict(function=lambda x: x.lower() == x), "UPPERCASE", False),
            (dict(function=lambda x: x.lower() == x), "lowercase", True),
        ],
    )
    def test_matches_string(self, rule_kwargs, match_against, result):
        rule = MatchRule(**rule_kwargs)
        assert rule.matches_string(match_against) == result

class TestTagNameMatchRule(SoupTest):

    @pytest.mark.parametrize(
        "rule_kwargs, tag_kwargs, result",
        [
            (dict(string="a"), dict(name="a"), True),
            (dict(string="a"), dict(name="ab"), False),

            (dict(pattern="a"), dict(name="a"), True),
            (dict(pattern="a"), dict(name="ab"), True),
            (dict(pattern="^a$"), dict(name="a"), True),
            (dict(pattern="^a$"), dict(name="ab"), False),

            # This isn't very useful, but it will work.
            (dict(present=True), dict(name="any random value"), True),
            (dict(present=False), dict(name="any random value"), False),

            (dict(function=lambda t: t.name in t.attrs),
             dict(name="id", attrs=dict(id="a")), True),

            (dict(function=lambda t: t.name in t.attrs),
             dict(name="id", attrs={"class":"a"}), False),
        ],
    )
    def test_matches_tag(self, rule_kwargs, tag_kwargs, result):
        rule = TagNameMatchRule(**rule_kwargs)
        tag = Tag(**tag_kwargs)
        assert rule.matches_tag(tag) == result

# AttributeValueMatchRule and StringMatchRule have the same
# logic as MatchRule.

class TestSoupStrainer(SoupTest):
    
    def test_constructor_string_deprecated_text_argument(self):
        with warnings.catch_warnings(record=True) as w:
            strainer = SoupStrainer(text="text")
            assert strainer.text == 'text'
            [warning] = w
            msg = str(warning.message)
            assert warning.filename == __file__
            assert msg == "The 'text' argument to the SoupStrainer constructor is deprecated. Use 'string' instead."

    def _match_function(x):
        pass
            
    def test_constructor(self):
        strainer = SoupStrainer(
            "tagname",
            {"attr1": "value"},
            string=self._match_function,
            attr2=["value1", False]
        )
        [name_rule] = strainer.name_rules
        assert name_rule == TagNameMatchRule(string="tagname")
        
        [attr1_rule] = strainer.attribute_rules.pop('attr1')
        assert attr1_rule == AttributeValueMatchRule(string="value")
        
        [attr2_rule1, attr2_rule2] = strainer.attribute_rules.pop('attr2')
        assert attr2_rule1 == AttributeValueMatchRule(string="value1")
        assert attr2_rule2 == AttributeValueMatchRule(present=False)
        
        assert not strainer.attribute_rules

        [string_rule] = strainer.string_rules
        assert string_rule == StringMatchRule(function=self._match_function)
        
    def test_scalar_attrs_becomes_class_restriction(self):
        # For the sake of convenience, passing a scalar value as
        # ``args`` results in a restriction on the 'class' attribute.
        strainer = SoupStrainer(attrs="mainbody")
        assert [] == strainer.name_rules
        assert [] == strainer.string_rules
        assert { "class": [AttributeValueMatchRule(string="mainbody")] } == (
            strainer.attribute_rules
        )
        
    def test_constructor_class_attribute(self):
        # The 'class' HTML attribute is also treated specially because
        # it's a Python reserved word. Passing in "class_" as a
        # keyword argument results in a restriction on the 'class'
        # attribute.
        strainer = SoupStrainer(class_="mainbody")
        assert [] == strainer.name_rules
        assert [] == strainer.string_rules
        assert { "class": [AttributeValueMatchRule(string="mainbody")] } == (
            strainer.attribute_rules
        )

        # But if you pass in "class_" as part of the ``attrs`` dict
        # it's not changed. (Otherwise there'd be no way to actually put
        # a restriction on an attribute called "class_".
        strainer = SoupStrainer(attrs=dict(class_="mainbody"))
        assert [] == strainer.name_rules
        assert [] == strainer.string_rules
        assert { "class_": [AttributeValueMatchRule(string="mainbody")] } == (
            strainer.attribute_rules
        )

    def test_constructor_with_overlapping_attributes(self):
        # If you specify the same attribute in arts and **kwargs, you end up
        # with two different AttributeValueMatchRule objects.

        # This happens whether you use the 'class' shortcut on attrs...
        strainer = SoupStrainer(attrs="class1", class_="class2")
        rule1, rule2 = strainer.attribute_rules['class']
        assert rule1.string == "class1"
        assert rule2.string == "class2"

        # Or explicitly specify the same attribute twice.
        strainer = SoupStrainer(attrs={"id": "id1"}, id="id2")
        rule1, rule2 = strainer.attribute_rules['id']
        assert rule1.string == "id1"
        assert rule2.string == "id2"
        
    @pytest.mark.parametrize(
        "obj, result",
        [
            ("a", MatchRule(string="a")),
            (b"a", MatchRule(string="a")),
            (True, MatchRule(present=True)),
            (False, MatchRule(present=False)),
            (re.compile("a"), MatchRule(pattern=re.compile("a"))),
            (_match_function, MatchRule(function=_match_function)),

            # Pass in a list and get back a list of rules.
            (["a", b"b"], [MatchRule(string="a"), MatchRule(string="b")]),
            ([re.compile("a"), _match_function],
             [MatchRule(pattern=re.compile("a")),
              MatchRule(function=_match_function)]),
            
            # Anything that doesn't fit is converted to a string.
            (100, MatchRule(string="100")),
        ]
    )
    def test__make_match_rules(self, obj, result):
        actual = list(SoupStrainer._make_match_rules(obj, MatchRule))
        # Helper to reduce the number of single-item lists in the
        # parameters.
        if len(actual) == 1:
            [actual] = actual
        assert result == actual

    @pytest.mark.parametrize(
        "cls, result", [
            (AttributeValueMatchRule, AttributeValueMatchRule(string="a")),
            (StringMatchRule, StringMatchRule(string="a")),
        ])
    def test__make_match_rules_different_classes(self, cls, result):
        actual = cls(string="a")
        assert actual == result
        
    def test__make_match_rules_nested_list(self):
        # If you pass a nested list into _make_match_rules, it's
        # ignored, to avoid the possibility of an infinite recursion.

        # Create a self-referential object.
        l = []
        l.append(l)

        with warnings.catch_warnings(record=True) as w:
            rules = SoupStrainer._make_match_rules(["a", l, "b"], MatchRule)
            assert list(rules) == [MatchRule(string="a"), MatchRule(string="b")]
            
            [warning] = w
            # Don't check the filename because the stacklevel is
            # designed for normal use and we're testing the private
            # method directly.
            msg = str(warning.message)
            assert msg == "Ignoring nested list [[...]] to avoid the possibility of infinite recursion."

    def tag_matches(
            self, strainer, name, attrs=None, string=None, prefix=None,
            match_valence=True
    ):
        # Create a Tag with the given prefix, name and attributes,
        # then make sure that strainer.matches_tag and allow_tag_creation
        # both approve it.
        tag = Tag(prefix=prefix, name=name, attrs=attrs)
        if string:
            tag.string = string
        return strainer.matches_tag(tag) and strainer.allow_tag_creation(prefix, name, attrs)

    def test_matches_tag_with_only_string(self):

        # A SoupStrainer that only has StringMatchRules won't ever
        # match a Tag.
        strainer = SoupStrainer(string=["a string", re.compile("string")])
        tag = Tag(name="b", attrs=dict(id="1"))
        tag.string = "a string"
        assert not strainer.matches_tag(tag)

        # There has to be a TagNameMatchRule or an
        # AttributeValueMatchRule as well.
        strainer.name_rules.append(TagNameMatchRule(string="b"))
        assert strainer.matches_tag(tag)

        strainer.name_rules = []
        strainer.attribute_rules['id'] = [AttributeValueMatchRule('1')]
        assert strainer.matches_tag(tag)
        
    def test_matches_tag_with_prefix(self):
        # If a tag has an attached namespace prefix, the tag's name is
        # tested both with and without the prefix.
        kwargs = dict(name="a", prefix="ns")

        assert self.tag_matches(SoupStrainer(name="a"), **kwargs)
        assert self.tag_matches(SoupStrainer(name="ns:a"), **kwargs)
        assert not self.tag_matches(SoupStrainer(name="ns2:a"), **kwargs)

    def test_one_name_rule_must_match(self):
        # If there are TagNameMatchRule, at least one must match.
        kwargs = dict(name="b")
        
        assert self.tag_matches(SoupStrainer(name="b"), **kwargs)
        assert not self.tag_matches(SoupStrainer(name="c"), **kwargs)
        assert self.tag_matches(
            SoupStrainer(name=["c", "d", "d", "b"]), **kwargs
        )
        assert self.tag_matches(
            SoupStrainer(name=[re.compile("c-f"), re.compile("[ab]$")]),
            **kwargs
        )
        
    def test_one_attribute_rule_must_match_for_each_attribute(self):
        # If there is one or more AttributeValueMatchRule for a given
        # attribute, at least one must match that attribute's
        # value. This is true for *every* attribute -- just matching one
        # attribute isn't enough.
        kwargs = dict(name="b", attrs={"class": "main", "id": "1"})

        # 'class' and 'id' match
        assert self.tag_matches(
            SoupStrainer(
                class_=["other", "main"], id=["20", "a", re.compile("^[0-9]")]
            ),
            **kwargs
        )

        # 'class' and 'id' are present and 'data' attribute is missing
        assert self.tag_matches(
            SoupStrainer(class_=True, id=True, data=False), **kwargs
        )
        
        # 'id' matches, 'class' does not.
        assert not self.tag_matches(
            SoupStrainer(class_=["other"], id=["2"]), **kwargs
        )

        # 'class' matches, 'id' does not
        assert not self.tag_matches(
            SoupStrainer(class_=["main"], id=["2"]), **kwargs
        )

        # 'class' and 'id' match but 'data' attribute is missing
        assert not self.tag_matches(
            SoupStrainer(class_=["main"], id=["1"], data=True),
            **kwargs
        )
        
    def test_match_against_multi_valued_attribute(self):
        # If an attribute has multiple values, only one of them
        # has to match the AttributeValueMatchRule.
        kwargs = dict(name="b", attrs={"class": ["main", "big"]})
        assert self.tag_matches(SoupStrainer(attrs="main"), **kwargs)
        assert self.tag_matches(SoupStrainer(attrs="big"), **kwargs)
        assert self.tag_matches(SoupStrainer(attrs=["main", "big"]), **kwargs)
        assert self.tag_matches(SoupStrainer(attrs=["big", "small"]), **kwargs)
        assert not self.tag_matches(SoupStrainer(attrs=["small", "smaller"]), **kwargs)
        
    def test_match_against_multi_valued_attribute_as_string(self):
        # If an attribute has multiple values, you can treat the entire
        # thing as one string during a match.
        kwargs = dict(name="b", attrs={"class": ["main", "big"]})
        assert self.tag_matches(SoupStrainer(attrs="main big"), **kwargs)

        # But you can't put them in any order; it's got to be the
        # order they are present in the Tag, which basically means the
        # order they were originally present in the document.
        assert not self.tag_matches(SoupStrainer(attrs=["big main"]), **kwargs)

    def test_one_string_rule_must_match(self):
        # If there's a TagNameMatchRule and/or an
        # AttributeValueMatchRule, then the StringMatchRule is _not_
        # ignored, and must match as well.
        tag = Tag(name="b", attrs=dict(id="1"))
        tag.string = "A string"

        assert SoupStrainer(name="b", string="A string").matches_tag(tag)
        assert not SoupStrainer(name="a", string="A string").matches_tag(tag)
        assert not SoupStrainer(name="a", string="Wrong string").matches_tag(tag)
        assert SoupStrainer(id="1", string="A string").matches_tag(tag)
        assert not SoupStrainer(id="2", string="A string").matches_tag(tag)
        assert not SoupStrainer(id="1", string="Wrong string").matches_tag(tag)

        assert SoupStrainer(name="b", id="1", string="A string").matches_tag(tag)

        # If there are multiple string rules, only one needs to match.
        assert SoupStrainer(
            name="b", id="1",
            string=["Wrong string", "Also wrong", re.compile("string")]
        ).matches_tag(tag)

    def test_deeply_nested_string(self):
        markup = "<a><b><div>a string<span>b string</b></div></b></a>"
        soup = self.soup(markup, parse_only=SoupStrainer(string=["a string", "b string"]))
        import pdb; pdb.set_trace()
        pass
        
        
    def test_documentation_examples(self):
        """Medium-weight real-world tests based on the Beautiful Soup
        documentation.
        """
        html_doc = """<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""
        only_a_tags = SoupStrainer("a")
        only_tags_with_id_link2 = SoupStrainer(id="link2")

        def is_short_string(string):
            return string is not None and len(string) < 10

        only_short_strings = SoupStrainer(string=is_short_string)

        a_soup = self.soup(html_doc, parse_only=only_a_tags)
        assert ('<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a><a class="sister" href="http://example.com/lacie" id="link2">Lacie</a><a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>'
                == a_soup.decode())

        id_soup = self.soup(html_doc, parse_only=only_tags_with_id_link2)
        assert (
            '<a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>'
            == id_soup.decode()
        )
        string_soup = self.soup(html_doc, parse_only=only_short_strings)
        assert '\n\n\nElsie,\nLacie and\nTillie\n...\n' == string_soup.decode()
