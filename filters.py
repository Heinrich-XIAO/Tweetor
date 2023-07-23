from datetime import datetime
from markupsafe import Markup

def format_flit(flit_content):
    formatted_content = flit_content.replace('***', '<strong><em>', 1).replace('***', '</em></strong>', 1)

    # Replace double asterisks (**) with HTML tags for bold
    formatted_content = formatted_content.replace('**', '<strong>', 1).replace('**', '</strong>', 1)

    # Replace single asterisks (*) with HTML tags for italic
    formatted_content = formatted_content.replace('*', '<em>', 1).replace('*', '</em>', 1)

    # Replace double underscores (__) with HTML tags for underline
    formatted_content = formatted_content.replace('__', '<u>', 1).replace('__', '</u>', 1)

    return Markup(formatted_content)

def format_timestamp(value):
    # Convert the timestamp to a datetime object
    timestamp = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    # Format the datetime object
    if timestamp.year != datetime.now().year:
        formatted_timestamp = timestamp.strftime("%B %d, %Y")
    else:
        formatted_timestamp = timestamp.strftime("%B %d")

    return formatted_timestamp