from cms import __version__ as cms_version
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.conf import settings
from django.forms.fields import CharField
from django.utils.translation import ugettext_lazy as _
from djangocms_text_tinymce.forms import TextForm
from djangocms_text_tinymce.models import Text
from djangocms_text_tinymce.utils import plugin_tags_to_user_html
from djangocms_text_tinymce.widgets import TextEditorWidget

class TextPlugin(CMSPluginBase):
    model = Text
    name = _("Text")
    form = TextForm
    render_template = "cms/plugins/text.html"
    change_form_template = "cms/plugins/text_plugin_change_form.html"

    def get_editor_widget(self, request):
        """
        Returns the Django form Widget to be used for
        the text area
        """
        return TextEditorWidget(profile=settings.TINYMCE_ADMIN_CONFIG)

    def get_form_class(self, request):
        """
        Returns a subclass of Form to be used by this plugin
        """
        # We avoid mutating the Form declared above by subclassing
        class TextPluginForm(self.form):
            pass
        widget = self.get_editor_widget(request)
        TextPluginForm.declared_fields["body"] = CharField(
            widget=widget, required=False, label=''
        )
        return TextPluginForm

    def get_form(self, request, obj=None, **kwargs):
        plugins = plugin_pool.get_text_enabled_plugins(
            self.placeholder,
            self.page
        )
        # pk = self.cms_plugin_instance.pk  # not used - removed since does not work
        form = self.get_form_class(request)
        kwargs['form'] = form  # override standard form
        return super(TextPlugin, self).get_form(request, obj, **kwargs)
#
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """
        We override the change form template path
        to provide backwards compatibility with CMS 2.x
        """
        if cms_version.startswith('2'):
            context['change_form_template'] = "admin/cms/page/plugin_change_form.html"
        return super(TextPlugin, self).render_change_form(request, context, add, change, form_url, obj)

    def render(self, context, instance, placeholder):
        context.update({
            'body': plugin_tags_to_user_html(
                instance.body,
                context,
                placeholder
            ),
            'placeholder': placeholder,
            'object': instance
        })
        return context

    def save_model(self, request, obj, form, change):
        obj.clean_plugins()
        super(TextPlugin, self).save_model(request, obj, form, change)

plugin_pool.register_plugin(TextPlugin)
