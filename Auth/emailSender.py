import logging
import os
from django.template import Template, Context
from django.utils.html import strip_tags
from django.utils.timezone import now, localtime
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from Authentication_System import settings


def _make_html_paragraphs(text):
    """Convert plaintext with newlines into safe HTML paragraphs."""
    from django.utils.html import escape

    lines = [ln.strip() for ln in (text or '').splitlines()]
    paragraphs = [
        f'<p style="margin:0 0 12px 0; color:#475569; line-height:1.6;">{escape(ln)}</p>'
        for ln in lines if ln
    ]

    return ''.join(paragraphs) or (
        '<p style="margin:0 0 12px 0; color:#475569;">No information provided.</p>'
    )


_HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{{ site_name }} - {{ short_title }}</title>
</head>

<body style="margin:0; padding:30px; background:#f1f5f9; font-family:Inter, Arial, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0"
style="background:#ffffff; border-radius:14px; overflow:hidden;
box-shadow:0 12px 35px rgba(15,23,42,0.08);">

<!-- HEADER -->
<tr>
<td style="padding:22px 28px; border-bottom:1px solid #e2e8f0;">
<table width="100%">
<tr>
<td>

<div style="display:flex; align-items:center; gap:12px;">
{% if logo_use_cid %}
<img src="cid:{{ logo_cid }}" style="height:42px;" />
{% elif logo_url %}
<img src="{{ logo_url }}" style="height:42px;" />
{% else %}
<div style="width:42px;height:42px;border-radius:10px;
background:#14b8c6;color:#ffffff;
display:flex;align-items:center;justify-content:center;
font-weight:700;font-size:18px;">
MD
</div>
{% endif %}

<div>
<div style="font-size:18px;font-weight:700;color:#0f172a;">
{{ site_name }}
</div>
<div style="font-size:12px;color:#64748b;">
Secure Authentication
</div>
</div>
</div>

</td>

<td align="right" style="font-size:12px;color:#64748b;">
{{ generation_date }}
</td>
</tr>
</table>
</td>
</tr>

<!-- BODY -->
<tr>
<td style="padding:32px 28px;">

<h2 style="margin:0 0 14px 0;
font-size:20px;
color:#0f172a;">
{{ title }}
</h2>

<div style="font-size:14px;color:#475569; line-height:1.6;">
{{ content_html|safe }}
</div>

{% if action_url %}
<div style="margin-top:22px;">
<a href="{{ action_url }}"
style="display:inline-block;
padding:12px 18px;
background:#14b8c6;
color:#ffffff;
border-radius:8px;
text-decoration:none;
font-weight:600;
box-shadow:0 6px 14px rgba(20,184,198,0.25);">
{{ action_text }}
</a>
</div>
{% endif %}

</td>
</tr>

<!-- FOOTER -->
<tr>
<td style="padding:18px 28px;
border-top:1px solid #e2e8f0;
font-size:12px;
color:#64748b;
text-align:center;">

If you didn’t request this action, you can safely ignore this email.<br/>
© {{ site_name }} {{ generation_date|slice:":4" }}

</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

logger = logging.getLogger(__name__)

def _send_styled_email(
    to_email,
    subject,
    title,
    content_plain,
    recipient_name=None,
    action_url=None,
    action_text="Voir",
    from_email=None
):
    from_email = from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@example.com"
    site_name = getattr(settings, "SITE_NAME", "MercenaryDev")
    site_url = getattr(settings, "SITE_URL", "")
    logo_url = getattr(settings, "EMAIL_LOGO_URL", None)
    attach_inline_logo = getattr(settings, "EMAIL_LOGO_PATH", None)

    content_html = _make_html_paragraphs(content_plain)

    ctx = {
        "site_name": site_name,
        "site_url": site_url,
        "logo_url": logo_url,
        "title": title,
        "short_title": title,
        "content_html": content_html,
        "recipient_name": recipient_name or "",
        "generation_date": localtime(now()).strftime("%d %B %Y %H:%M"),
        "action_url": action_url or "",
        "action_text": action_text,
        "logo_use_cid": False,
        "logo_cid": "logo_cid",
    }

    tmpl = Template(_HTML_TEMPLATE)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=content_plain,  # use plain text directly
            from_email=from_email,
            to=[to_email],
        )

        # Handle inline logo if exists
        if attach_inline_logo:
            logo_path = attach_inline_logo
            if not os.path.isabs(logo_path) and getattr(settings, "BASE_DIR", None):
                logo_path = os.path.join(settings.BASE_DIR, logo_path)

            if os.path.exists(logo_path):
                ctx["logo_use_cid"] = True
                html_content = tmpl.render(Context(ctx))
                msg.mixed_subtype = "related"
                msg.attach_alternative(html_content, "text/html")

                with open(logo_path, "rb") as f:
                    image = MIMEImage(f.read())
                image.add_header("Content-ID", "<logo_cid>")
                image.add_header("Content-Disposition", "inline", filename=os.path.basename(logo_path))
                msg.attach(image)
            else:
                logger.warning("Logo path not found: %s", logo_path)
                html_content = tmpl.render(Context(ctx))
                msg.attach_alternative(html_content, "text/html")
        else:
            html_content = tmpl.render(Context(ctx))
            msg.attach_alternative(html_content, "text/html")

        msg.send(fail_silently=False)
        return {"ok": True, "error": None}

    except Exception as exc:
        logger.exception("Email send failed: %s", exc)
        return {"ok": False, "error": exc}