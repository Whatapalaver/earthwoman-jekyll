# Earthwoman Blog

This blog was lost and then recovered from 1 old backup and the use of the Way Back Machine. It might take me a while to reformat all the old post currently held in drafts.

## TODO

- categories to be removed and replaced by tags
- missing images need to be found and uploaded
- favicon needs updating
- images need adding to frontmatter
- sort out full width images or sort wrapping

#### Full Width Image With Caption

To have wide images in posts or pages simply add #wide word with the hashtag at the end of image path like in the example below:

~~~~
{% include image-caption.html imageurl="/images/posts/Apple-Watch-In-Car.jpg#wide" 
title="Apple" caption="This is caption" %}
~~~~

Add the following code into your post/page markdown and change its attributes accordingly.

### Local Installation

To run locally `bundle exec jekyll serve` and navigate to localhost:4000

### Deployment

Sites built using Jekyll can be deployed in a large number of ways due to the static nature of the generated output. Here are some of the most common ways:

#### Manual Deployment

Jekyll generates your static site to the **_site** directory by default. You can transfer the contents of this directory to almost any hosting provider to get your site live. Here are some manual ways of achieving this:

##### Netlify

This theme is prepared to be hosted on [Netlify](https://www.netlify.com/). All you need to do is create a new private repository on GitHub or GitLab. Upload the theme to the repository and link your repo to Netlify. Please check [this link](https://www.netlify.com/blog/2015/10/28/a-step-by-step-guide-jekyll-3.0-on-netlify/#step-2-link-to-your-github) with the step by step guidelines.
