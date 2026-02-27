# Calculate PPM from this sample:

# CID,A,fc,foff,RXPWR,C,nRB,P,CrystalCorrectionFactor
# 22255,746M,6.22k,-19.7,N,255,U,UNK,1.0000083344691526044

# It's calculated like this:
# 1e6*(1-0.999997235615474378)

# Do it for the file in /home/lburlingham/pppm.csv (converted to CSV)
import pandas as pd

# read the csv file using pandas
csv_path = '<CSV_PATH>'
df = pd.read_csv(csv_path)

# use the last column of the DataFrame as the correction factor
# regardless of its name – the CSV always places the relevant value there.
ccf_col = df.columns[-1]
# if that column contains only NaNs (because the data rows were short),
# fall back to the previous column which likely holds the numeric value.
if df[ccf_col].isna().all() and len(df.columns) > 1:
    ccf_col = df.columns[-2]

print(f"using column '{ccf_col}' for ppm calculation")

# compute PPM for each row using a for loop and collect results
# when the chosen column is NaN for a specific row, fall back one column to
# the left (e.g. PR contains the real value when CrystalCorrectionFactor is
# missing in the row).
ppm_values = []
for row in df.itertuples(index=False):
    # use getattr to handle whichever column was selected
    value = getattr(row, ccf_col)
    # if the value is missing, try the previous column
    if pd.isna(value):
        # convert row to tuple to index; note row[0] is first field
        row_tuple = tuple(row)
        if len(row_tuple) >= 2:
            value = row_tuple[-2]
    try:
        ppm = 1e6 * (1 - float(value))
    except Exception:
        ppm = float('nan')
    ppm_values.append(ppm)

# add the computed values back into the DataFrame
df['PPM'] = ppm_values

# print the CID and computed PPM for each entry
print(df[['CID', 'PPM']])

# Get the average PPM
average_ppm = df['PPM'].mean()
print(f'Average PPM: {average_ppm}')