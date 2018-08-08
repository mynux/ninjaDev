#!/bin/python
#
# This script is trying to convert ghost database data, which is json formated and exported
# from ghost.db file via http://sqlitebrowser.org/. It tries to read the exported posts.json
# and generated jekyll markdown posts.
# 
# TAG: Migration-Tool; Ghost; Markdown
# 

import json
import io 
from datetime import datetime
import StringIO

with io.open('posts.json', encoding='utf-8') as f:
    all_posts = json.load(f)
    for post in all_posts:
        slug = post['slug']
        title = post['title']
        meta_title = post['meta_title']
        tags = meta_title.replace(' ', ', ') 
        content = post['markdown']
        # migrate content's image link.
        ghost_image_pattern = '/content/images'
        jekyll_image_pattern = '{{site.cdnurl}}/assets/images/posts'
        content_after = content.replace(ghost_image_pattern, jekyll_image_pattern)
        
        created_at_mills = post['created_at']
        created_at_sec = float(created_at_mills) / 1000.0
        created_date = datetime.fromtimestamp(created_at_sec).strftime('%Y-%m-%d %H:%M:%S.%f')

        post_name_prefix = datetime.fromtimestamp(created_at_sec).strftime('%Y-%m-%d-%H-%M')
        post_name_title = slug
        post_name = post_name_prefix + "-" + post_name_title + ".markdown"

	layout_slash = '---'
        output = StringIO.StringIO()
        output.write(layout_slash + "\n")
        output.write("title: " + title + "\n")
        output.write("layout: post\n")
        output.write("tags: [" + tags + "]\n")
        output.write("date: " + created_date + "\n")
        output.write(layout_slash + "\n")
        output.write(content_after)
        output.write("\n")
        with io.open(post_name, 'w', encoding='utf-8') as w:
             w.write(unicode(output.getvalue()))
        
