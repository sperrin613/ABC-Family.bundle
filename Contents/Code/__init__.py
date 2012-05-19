RE_SEASON = Regex('s([0-9]+)')
RE_EPISODE = Regex('e([0-9]+)')
RE_DURATION = Regex('Duration: ([0-9]+:[0-9]{2})')

##################################################################################################ABC
PLUGIN_PREFIX = "/video/abcfamily"
NAME          = "ABC Family"

ABC_ROOT      = "http://abc.go.com/"
SHOW_LIST     = "http://cdn.abc.go.com/vp2/ws-supt/s/syndication/2000/rss/002/001/-1/-1/-1/-1/-1/-1"
EPISODE_LIST  = "http://cdn.abc.go.com/vp2/ws-supt/s/syndication/2000/rss/002/001/lf/-1/%s/-1/-1/-1"
FEED_URL      = "http://cdn.abc.go.com/vp2/ws/s/contents/2000/utils/mov/13/9024/%s/432"
ART_URL       = "http://cdn.media.abc.go.com/m/images/shows/%s/bg/bkgd.jpg"

ART           = "art-default.jpg"
ICON          = "icon-default.jpg"

####################################################################################################
def Start():
    Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, NAME, ICON, ART)

    ObjectContainer.title1 = NAME
    
    ObjectContainer.art = R(ART)
    DirectoryObject.thumb = R(ICON)

    DirectoryItem.Object = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13"

####################################################################################################
def MainMenu():
    oc = ObjectContainer()
    content = XML.ElementFromURL(SHOW_LIST)
    for item in content.xpath('//item'):
        title = item.xpath('./title')[0].text
        titleUrl = item.xpath('./link')[0].text
        description = HTML.ElementFromString(item.xpath('./description')[0].text)
        thumb = item.xpath('./image')[0].text
        summary = description.xpath('.//p')[0].text
        showId = titleUrl.split('?')[0]
        showId = showId.rsplit('/', 1)[1]
        oc.add(DirectoryObject(key=Callback(VideoPage, showId=showId, title=title), title=title, summary=summary,
            thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
    return oc

####################################################################################################
def VideoPage(showId, title):
    oc = ObjectContainer(title2=title)
    episodeRss = EPISODE_LIST % (showId)
    content = XML.ElementFromURL(episodeRss)
    for item in content.xpath('//item'):
        link = item.xpath('./link')[0].text
        title1 = item.xpath('./title')[0].text
        ep_title = title1.split(' Full Episode')[0]
        season = RE_SEASON.findall(title1.split(' Full Episode')[-1])[0]
        episode = RE_EPISODE.findall(title1.split(' Full Episode')[-1])[0]
        description = HTML.ElementFromString(item.xpath('./description')[0].text)
        thumb = description.xpath('.//img')[0].get('src')
        summary = description.xpath('.//p')[0].text
        runtime = RE_DURATION.search(item.xpath('./description')[0].text).group(1)
        duration = DurationMS(runtime)
        
        oc.add(EpisodeObject(url=link, title=ep_title, show=title, season=int(season), index=int(episode), summary=summary,
            duration=duration, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
    return oc
    
####################################################################################################
def DurationMS(runtime):
    parts = runtime.split(':')
    duration = (int(parts[0])*60 + int(parts[1]))*1000
    return duration