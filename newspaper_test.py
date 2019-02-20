from newspaper import Article

url = 'https://www.ifanr.com/1174322'
article = Article(url, language='zh')
article.download()
article.parse()
print(article.authors)
print(article.publish_date)
print(article.text)
print(article.top_image)
print(article.movies)
print('--------')
article.nlp()
article.keywords
article.summary
