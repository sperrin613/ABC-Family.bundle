NAME = "ABC Family"
SHOW_LIST = "http://cdn.abc.go.com/vp2/ws-supt/s/syndication/2000/rss/002/001/-1/-1/-1/-1/-1/-1"
EPISODE_LIST = "http://cdn.abc.go.com/vp2/ws-supt/s/syndication/2000/rss/002/001/lf/-1/%s/-1/-1/-1"

RE_SXX_EXX = Regex('e(\d+) \| s(\d+)')
RE_DURATION = Regex('Duration: (\d+:\d{2})')
RE_AIRDATE = Regex('Air date:.+?, (\d{2}.+?20\d{2})')

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'

####################################################################################################
@handler('/video/abcfamily', NAME)
def MainMenu():

	oc = ObjectContainer()

	if not Client.Platform in ('Android', 'iOS', 'Roku') and not (Client.Platform == 'Safari' and Platform.OS == 'MacOSX'):
		oc.header = 'Not supported'
		oc.message = 'This channel is not supported on %s' % (Client.Platform if Client.Platform is not None else 'this client')
		return oc

	xml = XML.ElementFromURL(SHOW_LIST)

	for item in xml.xpath('//item'):
		title = item.xpath('./title/text()')[0]

		if 'movies' in title.lower():
			continue

		show_id = item.xpath('./link/text()')[0].split('?')[0].split('/')[-1]
		summary = HTML.ElementFromString(item.xpath('./description/text()')[0]).xpath('//p/text()')[0]

		try:
			thumb = item.xpath('./image/text()')[0]
		except:
			thumb = ''

		oc.add(DirectoryObject(
			key = Callback(Episodes, show_id=show_id, title=title),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb)
		))

	return oc

####################################################################################################
@route('/video/abcfamily/episodes')
def Episodes(show_id, title):

	oc = ObjectContainer(title2=title)
	xml = XML.ElementFromURL(EPISODE_LIST % show_id)

	for item in xml.xpath('//item'):
		url = item.xpath('./link/text()')[0]
		full_title = item.xpath('./title/text()')[0]
		ep_title = full_title.split(' Full Episode')[0]
		# Found that one show had an episode value of "Recap" and gave an error when trying to pull this data
		try:
			(episode, season) = RE_SXX_EXX.search(full_title).groups()
			episode = int(episode)
			season = int(season)
		except:
			(episode, season) = (None, None)

		description = HTML.ElementFromString(item.xpath('./description/text()')[0])

		summary = description.xpath('.//p/text()')[0]
		thumb = description.xpath('.//img/@src')[0]

		duration = RE_DURATION.search(item.xpath('./description/text()')[0]).group(1)
		duration = Datetime.MillisecondsFromString(duration)

		originally_available_at = RE_AIRDATE.search(item.xpath('./description/text()')[0]).group(1)
		originally_available_at = Datetime.ParseDate(originally_available_at).date()

		oc.add(EpisodeObject(
			url = url,
			title = ep_title,
			show = title,
			season = season,
			index = episode,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb),
			duration = duration,
			originally_available_at = originally_available_at
		))

	return oc
