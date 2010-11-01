
from django import template
from django.utils.functional import curry
from functools import wraps
from inspect import getargspec

class Library(template.Library):
    """
    Extends django.template.Library providing several shortcuts that attempt 
    to take the leg-work out of creating different types of template tags.
    """

    def as_tag(self, takes_context=False):
        """
        Creates a tag expecting the format: ``{% tag_name as var_name %}``
        The decorated func returns the value that is given to ``var_name`` in
        the template.
        """
        def dec(tag_func):
            @wraps(tag_func)
            def tag_wrapper(parser, token):
                class AsTagNode(template.Node):
                    def render(self, context):
                        parts = token.split_contents()
                        args = parts[1:-2]
                        if takes_context:
                            args.insert(0, context)
                        context[parts[-1]] = tag_func(*args)
                        return ""
                return AsTagNode()
            return self.tag(tag_wrapper)
        if callable(takes_context):
            tag_func = takes_context
            takes_context = False
            return dec(tag_func)
        return dec

    def render_tag(self, tag_func):
        """
        Creates a tag using the decorated func as the render function for the
        template tag node. The render function takes two arguments - the
        template context and the tag token.
        """
        @wraps(tag_func)
        def tag_wrapper(parser, token):
            class RenderTagNode(template.Node):
                def render(self, context):
                    return tag_func(context, token)
            return RenderTagNode()
        return self.tag(tag_wrapper)

    def to_end_tag(self, tag_func):
        """
        Creates a tag that parses until it finds the corresponding end tag,
        eg: for a tag named ``mytag`` it will parse until ``endmytag``.
        The decorated func's return value is used to render the parsed
        content and takes three arguments - the parsed nodelist between the
        start and end tags, the template context and the tag token.
        """
        @wraps(tag_func)
        def tag_wrapper(parser, token):
            class ToEndTagNode(template.Node):
                def __init__(self):
                    end_name = "end%s" % tag_func.__name__
                    self.nodelist = parser.parse((end_name,))
                    parser.delete_first_token()
                def render(self, context):
                    context.push()
                    args = (context, self.nodelist, token, parser)
                    value = tag_func(*args[:tag_func.func_code.co_argcount])
                    context.pop()
                    return value
            return ToEndTagNode()
        return self.tag(tag_wrapper)

    def simple_context_tag(self, func):
        params, xx, xxx, defaults = getargspec(func)

        class SimpleContextNode(template.Node):
            def __init__(self, vars_to_resolve):
                self.vars_to_resolve = map(template.Variable, vars_to_resolve)

            def render(self, context):
                resolved_vars = [var.resolve(context) for var in self.vars_to_resolve]
                return func(context, *resolved_vars)

        compile_func = curry(template.generic_tag_compiler, params, defaults, getattr(func, "_decorated_function", func).__name__, SimpleContextNode)
        compile_func.__doc__ = func.__doc__
        self.tag(getattr(func, "_decorated_function", func).__name__, compile_func)
        return func

