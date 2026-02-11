import pandas as pd

df = pd.read_excel('data_(tuha peuet gampong).xlsx', header=None)

# Show rows around BUKET MEDANG ARA section (rows 7-25)
print("=== BUKET MEDANG ARA section ===")
for r in range(7, 25):
    row_data = [str(df.iloc[r, c])[:30] if pd.notna(df.iloc[r, c]) else '_EMPTY_' for c in range(min(11, len(df.columns)))]
    print(f"  Row {r}: {row_data}")

# Find Sekretaris patterns
print("\n=== All rows with 'Sekretaris' or 'sekretaris' ===")
for i in range(len(df)):
    for c in range(min(11, len(df.columns))):
        val = df.iloc[i, c]
        if pd.notna(val) and 'ekretaris' in str(val):
            # Show this row and next 2
            for r in range(max(0,i-1), min(len(df), i+3)):
                row_data = [str(df.iloc[r, c2])[:30] if pd.notna(df.iloc[r, c2]) else '_EMPTY_' for c2 in range(min(11, len(df.columns)))]
                marker = " <<< SEKRETARIS" if r == i else ""
                print(f"  Row {r}: {row_data}{marker}")
            print()
            break

# Show MATANG SEUTUI section
print("\n=== MATANG SEUTUI section ===")
for i in range(len(df)):
    for c in range(min(11, len(df.columns))):
        val = df.iloc[i, c]
        if pd.notna(val) and 'MATANG SEUTUI' in str(val).upper():
            for r in range(i, min(len(df), i+12)):
                row_data = [str(df.iloc[r, c2])[:30] if pd.notna(df.iloc[r, c2]) else '_EMPTY_' for c2 in range(min(11, len(df.columns)))]
                print(f"  Row {r}: {row_data}")
            break
    else:
        continue
    break
