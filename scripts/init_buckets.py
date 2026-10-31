from wa.storage import ensure_buckets

if __name__ == "__main__":
    created = ensure_buckets()
    print(f"created: {created}" if created else "buckets already exist")
