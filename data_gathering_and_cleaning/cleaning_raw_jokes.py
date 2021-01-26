import json

def clean(source_fn, destination_fn):
    with open(source_fn) as f:
        data = json.load(f)

    seen_ids = set()

    duplicates = 0
    removed = 0
    cleaned_posts = []
    for post in data:
        # Post is duplicate based on id.
        if post["id"] in cleaned_posts:
            duplicates += 1
            
        else:
            seen_ids.add(post["id"])
            # Title or body has been deleted (usually for TOS violation)
            if post["title"] in ["[removed]", "[deleted]"] or post["body"] in ["[removed]", "[deleted]"]:
                removed += 1
            # Post fits all criteria to be saved.
            # TODO Can add more post filtering rules here if necessary
            else:
                keys = ["body", "id", "score", "title"]
                clean_post = { key: post[key] for key in keys }
                cleaned_posts.append(clean_post)


    print(f'Total cleaned posts: {len(cleaned_posts)}')
    print(f'Duplicates: {duplicates}')
    print(f'Removed/deleted: {removed}')

    with open(destination_fn, 'w') as f:
        json.dump(cleaned_posts, f, indent=4)
        print(f'Saved cleaned posts to: {destination_fn}')

# clean(source_fn="data/r_cleanjokes_uncleaned.json", destination_fn="data/reddit_cleanjokes.json")
# clean(source_fn="data/r_DirtyJokes_uncleaned.json", destination_fn="data/reddit_DirtyJokes.json")
clean(source_fn="data/r_jokes_2021_uncleaned.json", destination_fn="data/reddit_jokes.json")