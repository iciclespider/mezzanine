
from django.conf import settings
from django.utils.translation import ugettext as _
from mezzanine.configuration import register_setting
import os.path


register_setting(
    name="DEBUG",
    description=_("If ``True``, 404s and 500s debug views are displayed."),
    editable=True,
    default=True,
)

register_setting(
    name="TEMPLATE_BLOGPOST",
    description=_("Template for all blog post views."),
    editable=True,
    default="base/blogpost.html",
)

register_setting(
    name="TEMPLATE_BLOGPAGE",
    description=_("Template for all blog page views."),
    editable=True,
    default="base/blogpage.html",
)

register_setting(
    name="TEMPLATE_STAFFPAGE",
    description=_("Template for all staff page views."),
    editable=True,
    default="base/staffpage.html",
)

register_setting(
    name="TEMPLATE_FORMPAGE",
    description=_("Template for all form page views."),
    editable=True,
    default="base/formpage.html",
)

register_setting(
    name="TEMPLATE_CONTENTPAGE",
    description=_("Template for all content page views."),
    editable=True,
    default="base/contentpage.html",
)

register_setting(
    name="TEMPLATE_DISPLAYABLE",
    description=_("Template for all displayable views."),
    editable=True,
    default="base/displayable.html",
)

register_setting(
    name="TEMPLATE_SITE",
    description=_("Site template for all all views."),
    editable=True,
    default="base/site.html",
)

register_setting(
    name="TEMPLATE_BODY",
    description=_("Body template for all views."),
    editable=True,
    default="base/body.html",
)

register_setting(
    name="TEMPLATE_HTML",
    description=_("HTML template for all views."),
    editable=True,
    default="base/html.html",
)

register_setting(
    name="TEMPLATE_404",
    description=_("Template for 404s."),
    editable=True,
    default="base/404.html",
)

register_setting(
    name="TEMPLATE_500",
    description=_("Template for 500s."),
    editable=True,
    default="base/500.html",
)

register_setting(
    name="JQUERY_UI_THEME",
    description=_("jQuery UI Theme to use."),
    editable=True,
    default="base",
)

register_setting(
    name="STYLE_BODY",
    description=_("Body CSS Style for all views."),
    editable=True,
    default="",
)

register_setting(
    name="STYLE_SITE",
    description=_("Site CSS Style for all views."),
    editable=True,
    default="base/site.ccss",
)

register_setting(
    name="STYLE_DISPLAYABLE",
    description=_("CSS Style for all displayable views."),
    editable=True,
    default="",
)

register_setting(
    name="STYLE_CONTENTPAGE",
    description=_("CSS Style for all content page views."),
    editable=True,
    default="",
)

register_setting(
    name="STYLE_STAFFPAGE",
    description=_("CSS Style for all staff page views."),
    editable=True,
    default="",
)

register_setting(
    name="STYLE_FORMPAGE",
    description=_("CSS Style for all form page views."),
    editable=True,
    default="",
)

register_setting(
    name="STYLE_BLOGPAGE",
    description=_("CSS Style for all blog page views."),
    editable=True,
    default="",
)

register_setting(
    name="STYLE_BLOGPOST",
    description=_("CSS Style for all blog post views."),
    editable=True,
    default="",
)

register_setting(
    name="GOOGLE_ANALYTICS_ID",
    editable=True,
    description=_("Google Analytics ID (http://www.google.com/analytics/)"),
    default="",
)

#register_setting(
#    name="BLOG_BITLY_USER",
#    description=_("Username for bit.ly URL shortening service."),
#    editable=True,
#    default="",
#)

#register_setting(
#    name="BLOG_BITLY_KEY",
#    description=_("Key for bit.ly URL shortening service."),
#    editable=True,
#    default="",
#)

#register_setting(
#    name="COMMENTS_DISQUS_SHORTNAME",
#    description=_("Username for the http://disqus.com comments service."),
#    editable=True,
#    default="",
#)

#register_setting(
#    name="COMMENTS_DISQUS_KEY",
#    description=_("API key for the http://disqus.com comments service."),
#    editable=True,
#    default="",
#)

#register_setting(
#    name="COMMENTS_NUM_LATEST",
#   description=_("Number of latest comments to show in the admin dashboard."),
#   editable=True,
#    default=5,
#)

#register_setting(
#    name="COMMENTS_UNAPPROVED_VISIBLE",
#    description=_("If ``True``, unapproved comments will have a placeholder "
#       "visible on the site with a 'waiting for approval' or "
#        "'comment removed' message based on the workflow around the "
#        "``MEZZANINE_COMMENTS_DEFAULT_APPROVED`` setting - if ``True`` then "
#       "the former message is used, if ``False`` then the latter."),
#    editable=True,
#    default=True,
#)

#register_setting(
#    name="TAG_CLOUD_SIZES",
#    description=_("Number of different sizes for tags when shown as a cloud."),
#    editable=True,
#    default=4,
#)

#register_setting(
#    name="PAGES_MENU_SHOW_ALL",
#    description=_("If ``True``, the pages menu will show all levels of "
#        "navigation, otherwise child pages are only shown when viewing the "
#        "parent page."),
#    editable=True,
#    default=True,
#)

#register_setting(
#    name="SEARCH_PER_PAGE",
#    description=_("Number of results to show in the search results page."),
#    editable=True,
#    default=10,
#)

#register_setting(
#    name="SEARCH_MAX_PAGING_LINKS",
#    description=_("Max number of paging links for the search results page."),
#    editable=True,
#    default=10,
#)

register_setting(
    name="ADMIN_MENU_ORDER",
    description=_("Controls the ordering and grouping of the admin menu."),
    editable=False,
    default=(
        (_("Content"), ("pages.Page", "staff.Person", "core.Template",
            (_("Media Library"), "fb_browse"))),
        (_("Blogs"), ("blog.Post", "blog.Comment")),
        (_("Settings"), ("configuration.Settings", "sites.Site")),
        (_("Users"), ("auth.User",)),
    ),
)

register_setting(
    name="ADMIN_REMOVAL",
    description=_("Unregister these models from the admin."),
    editable=False,
    default=('django.contrib.auth.models.Group',),
)

register_setting(
    name="FORMS_FIELD_MAX_LENGTH",
    description=_("Max length allowed for field values in the forms app."),
    editable=False,
    default=2000,
)

register_setting(
    name="FORMS_LABEL_MAX_LENGTH",
    description=_("Max length allowed for field labels in the forms app."),
    editable=False,
    default=200,
)

register_setting(
    name="FORMS_UPLOAD_ROOT",
    description=_("Absolute path for storing file uploads for the forms app."),
    editable=False,
    default="",
)

register_setting(
    name="MOBILE_USER_AGENTS",
    description=_("Strings to search user agent for when testing for a "
        "mobile device."),
    editable=False,
    default=(
        "2.0 MMP", "240x320", "400X240", "AvantGo", "BlackBerry",
        "Blazer", "Cellphone", "Danger", "DoCoMo", "Elaine/3.0",
        "EudoraWeb", "Googlebot-Mobile", "hiptop", "IEMobile",
        "KYOCERA/WX310K", "LG/U990", "MIDP-2.", "MMEF20", "MOT-V",
        "NetFront", "Newt", "Nintendo Wii", "Nitro", "Nokia",
        "Opera Mini", "Palm", "PlayStation Portable", "portalmmm",
        "Proxinet", "ProxiNet", "SHARP-TQ-GX10", "SHG-i900",
        "Small", "SonyEricsson", "Symbian OS", "SymbianOS",
        "TS21i-10", "UP.Browser", "UP.Link", "webOS", "Windows CE",
        "WinWAP", "YahooSeeker/M1A1-R2D2", "iPhone", "iPod", "Android",
        "BlackBerry9530", "LG-TU915 Obigo", "LGE VX", "webOS",
        "Nokia5800",
    ),
)

register_setting(
    name="DASHBOARD_TAGS",
    description=_("A three item sequence, each containing a sequence of "
        "template tags used to render the admin dashboard."),
    editable=False,
    default=(
        ("blog_tags.quick_blog", "mezzanine_tags.app_list"),
        ("blog_tags.recent_comments",),
        ("mezzanine_tags.recent_actions",),
    ),
)

register_setting(
    name="CONTENT_MEDIA_PATH",
    description=_("Absolute path to Mezzanine's internal media files."),
    editable=False,
    default=os.path.join(os.path.dirname(__file__), "..", "core", "media"),
)

register_setting(
    name="CONTENT_MEDIA_URL",
    description=_("URL prefix for serving Mezzanine's internal media files."),
    editable=False,
    default="/content_media/",
)

register_setting(
    name="STOP_WORDS",
    description=_("List of words which will be stripped from search queries."),
    editable=False,
    default=(
        "a", "about", "above", "above", "across", "after",
        "afterwards", "again", "against", "all", "almost", "alone",
        "along", "already", "also", "although", "always", "am",
        "among", "amongst", "amoungst", "amount", "an", "and",
        "another", "any", "anyhow", "anyone", "anything", "anyway",
        "anywhere", "are", "around", "as", "at", "back", "be",
        "became", "because", "become", "becomes", "becoming", "been",
        "before", "beforehand", "behind", "being", "below", "beside",
        "besides", "between", "beyond", "bill", "both", "bottom",
        "but", "by", "call", "can", "cannot", "cant", "co", "con",
        "could", "couldnt", "cry", "de", "describe", "detail", "do",
        "done", "down", "due", "during", "each", "eg", "eight",
        "either", "eleven", "else", "elsewhere", "empty", "enough",
        "etc", "even", "ever", "every", "everyone", "everything",
        "everywhere", "except", "few", "fifteen", "fify", "fill",
        "find", "fire", "first", "five", "for", "former", "formerly",
        "forty", "found", "four", "from", "front", "full", "further",
        "get", "give", "go", "had", "has", "hasnt", "have", "he",
        "hence", "her", "here", "hereafter", "hereby", "herein",
        "hereupon", "hers", "herself", "him", "himself", "his",
        "how", "however", "hundred", "ie", "if", "in", "inc",
        "indeed", "interest", "into", "is", "it", "its", "itself",
        "keep", "last", "latter", "latterly", "least", "less", "ltd",
        "made", "many", "may", "me", "meanwhile", "might", "mill",
        "mine", "more", "moreover", "most", "mostly", "move", "much",
        "must", "my", "myself", "name", "namely", "neither", "never",
        "nevertheless", "next", "nine", "no", "nobody", "none",
        "noone", "nor", "not", "nothing", "now", "nowhere", "of",
        "off", "often", "on", "once", "one", "only", "onto", "or",
        "other", "others", "otherwise", "our", "ours", "ourselves",
        "out", "over", "own", "part", "per", "perhaps", "please",
        "put", "rather", "re", "same", "see", "seem", "seemed",
        "seeming", "seems", "serious", "several", "she", "should",
        "show", "side", "since", "sincere", "six", "sixty", "so",
        "some", "somehow", "someone", "something", "sometime",
        "sometimes", "somewhere", "still", "such", "system", "take",
        "ten", "than", "that", "the", "their", "them", "themselves",
        "then", "thence", "there", "thereafter", "thereby",
        "therefore", "therein", "thereupon", "these", "they",
        "thickv", "thin", "third", "this", "those", "though",
        "three", "through", "throughout", "thru", "thus", "to",
        "together", "too", "top", "toward", "towards", "twelve",
        "twenty", "two", "un", "under", "until", "up", "upon", "us",
        "very", "via", "was", "we", "well", "were", "what", "whatever",
        "when", "whence", "whenever", "where", "whereafter", "whereas",
        "whereby", "wherein", "whereupon", "wherever", "whether",
        "which", "while", "whither", "who", "whoever", "whole", "whom",
        "whose", "why", "will", "with", "within", "without", "would",
        "yet", "you", "your", "yours", "yourself", "yourselves", "the",
    ),
)

register_setting(
    name="TINYMCE_URL",
    description=_("URL prefix for serving Tiny MCE files."),
    editable=False,
    default="%stinymce" % settings.ADMIN_MEDIA_PREFIX,
)

register_setting(
    name="COMMENTS_DEFAULT_APPROVED",
    description=_("If ``True``, built-in comments are approved by default."),
    editable=False,
    default=True,
)

register_setting(
    name="BLOG_POSTS_PER_PAGE",
    description=_("Number of blog posts to show on a blog listing page."),
    editable=True,
    default=5,
)

register_setting(
    name="BLOG_MAX_PAGING_LINKS",
    description=_("Max number of paging links to show on a blog listing page."),
    editable=True,
    default=10,
)

