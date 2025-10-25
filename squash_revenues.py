import json
from collections import defaultdict
import os

def squash_revenues(input_file):
    """
    Squashes revenue entries by the same person on a single day and of the same type into a single entry.
    The original file is renamed with a .bak extension.
    """
    with open(input_file, 'r') as f:
        revenues = json.load(f)

    # Use a dictionary to group revenues by date, primary client, and type
    grouped_revenues = defaultdict(list)
    for revenue in revenues:
        if revenue.get('clients'):
            # Create a unique key for each date, client, and type
            key = (revenue['date'], revenue['clients'][0], revenue['type'])
            grouped_revenues[key].append(revenue)

    squashed_list = []
    processed_groups = set()

    for revenue in revenues:
        if not revenue.get('clients'):
            squashed_list.append(revenue)
            continue

        key = (revenue['date'], revenue['clients'][0], revenue['type'])
        if key in processed_groups:
            continue

        group = grouped_revenues.get(key)
        if not group:
            squashed_list.append(revenue)
            continue
            
        processed_groups.add(key)

        if len(group) == 1:
            squashed_list.append(group[0])
            continue

        # Aggregate data for the squashed entry
        total_amount = sum(item['amount'] for item in group)
        comments = ", ".join(item['comments'] for item in group if item.get('comments'))
        
        # Handle the 'source' field aggregation
        source_counts = defaultdict(int)
        for item in group:
            source_counts[item['source']] += 1
        
        source_parts = []
        for src, count in source_counts.items():
            if count > 1:
                source_parts.append(f"{src} x{count}")
            else:
                source_parts.append(src)
        source = ", ".join(source_parts)

        # Create the new squashed entry
        squashed_entry = {
            'id': group[0]['id'],  # Keep the ID of the first entry in the group
            'source': source,
            'amount': total_amount,
            'date': key[0],
            'type': key[2],
            'clients': [key[1]],
            'comments': comments
        }
        squashed_list.append(squashed_entry)

    # Sort the final list by date
    squashed_list.sort(key=lambda x: x['date'])

    # Rename original file to .bak
    backup_file = input_file + '.bak'
    if os.path.exists(backup_file):
        os.remove(backup_file)
    os.rename(input_file, backup_file)

    # Write the squashed data to the original filename
    with open(input_file, 'w') as f:
        json.dump(squashed_list, f, indent=2)

if __name__ == '__main__':
    input_filename = 'revenues.json'
    squash_revenues(input_filename)
    print(f"Revenues in '{input_filename}' have been squashed. Original file saved as '{input_filename}.bak'")
