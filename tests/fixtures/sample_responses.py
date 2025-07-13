"""
Sample API responses for testing
"""

TMDB_MOVIE_RESPONSE = {
    "results": [
        {
            "adult": False,
            "backdrop_path": "/fCayJrkfRaCRCTh8GqN30f8oyQF.jpg",
            "genre_ids": [28, 878],
            "id": 603,
            "original_language": "en",
            "original_title": "The Matrix",
            "overview": "Set in the 22nd century...",
            "popularity": 98.174,
            "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "release_date": "1999-03-31",
            "title": "The Matrix",
            "video": False,
            "vote_average": 8.2,
            "vote_count": 20671,
        }
    ]
}

TMDB_TV_RESPONSE = {
    "results": [
        {
            "backdrop_path": "/9faGSFi5jam6pDWGNd0p8JcJgXQ.jpg",
            "first_air_date": "2008-01-20",
            "genre_ids": [18, 80],
            "id": 1396,
            "name": "Breaking Bad",
            "origin_country": ["US"],
            "original_language": "en",
            "original_name": "Breaking Bad",
            "overview": "When Walter White, a New Mexico chemistry teacher...",
            "popularity": 385.504,
            "poster_path": "/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
            "vote_average": 8.9,
            "vote_count": 8477,
        }
    ]
}

TMDB_EPISODE_RESPONSE = {
    "air_date": "2008-01-20",
    "episode_number": 1,
    "id": 62085,
    "name": "Pilot",
    "overview": "Walter White, a struggling high school chemistry teacher...",
    "production_code": "",
    "runtime": 58,
    "season_number": 1,
    "show_id": 1396,
    "still_path": "/ydlY3iPfeOAvu8gVqrxPoMvzNCn.jpg",
    "vote_average": 7.7,
    "vote_count": 117,
}

TVDB_SEARCH_RESPONSE = {
    "data": [
        {
            "series": {
                "id": 81189,
                "name": "Breaking Bad",
                "slug": "breaking-bad",
                "image": "https://artworks.thetvdb.com/banners/graphical/81189-g8.jpg",
                "nameTranslations": ["eng"],
                "overviewTranslations": ["eng"],
                "aliases": [],
                "firstAired": "2008-01-20",
                "lastAired": "2013-09-29",
                "nextAired": "",
                "score": 80932,
                "status": {
                    "id": 3,
                    "name": "Ended",
                    "recordType": "series",
                    "keepUpdated": False,
                },
                "originalCountry": "usa",
                "originalLanguage": "eng",
                "defaultSeasonType": 1,
                "isOrderRandomized": False,
                "lastUpdated": "2021-04-20 12:34:56",
                "averageRuntime": 47,
                "episodes": None,
                "overview": "Breaking Bad is an American crime drama television series...",
            }
        }
    ]
}

TVDB_EPISODE_RESPONSE = {
    "data": {
        "episodes": [
            {
                "id": 349232,
                "seriesId": 81189,
                "name": "Pilot",
                "aired": "2008-01-20",
                "runtime": 58,
                "nameTranslations": ["eng"],
                "overviewTranslations": ["eng"],
                "image": "https://artworks.thetvdb.com/banners/episodes/81189/349232.jpg",
                "imageType": 12,
                "isMovie": 0,
                "seasons": None,
                "number": 1,
                "seasonNumber": 1,
                "lastUpdated": "2021-04-20 12:34:56",
                "finaleType": None,
                "overview": "Walter White, a struggling high school chemistry teacher...",
            }
        ]
    }
}

GUESSIT_MOVIE_RESULT = {
    "title": "The Matrix",
    "year": 1999,
    "type": "movie",
    "container": "mkv",
    "video_codec": "x264",
    "resolution": "1080p",
    "source": "BluRay",
}

GUESSIT_TV_RESULT = {
    "title": "Breaking Bad",
    "season": 1,
    "episode": 1,
    "type": "episode",
    "container": "mkv",
    "video_codec": "x264",
    "resolution": "720p",
    "source": "HDTV",
}

GUESSIT_EDGE_CASES = {
    "movie_with_dots": {
        "title": "Movie with dots in title",
        "year": 2020,
        "type": "movie",
        "container": "mkv",
    },
    "tv_with_episode_title": {
        "title": "TV Show",
        "season": 1,
        "episode": 1,
        "episode_title": "Episode with (parentheses)",
        "type": "episode",
        "container": "mp4",
    },
    "movie_with_brackets": {
        "title": "Movie",
        "year": 2021,
        "type": "movie",
        "container": "avi",
        "edition": "Special Edition",
    },
    "show_with_underscores": {
        "title": "Show with underscores",
        "season": 1,
        "episode": 1,
        "type": "episode",
        "container": "mkv",
    },
    "multiple_years": {
        "title": "Movie",
        "year": 2020,
        "type": "movie",
        "container": "mkv",
    },
}
