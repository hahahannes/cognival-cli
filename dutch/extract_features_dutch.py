import csv
from tqdm import tqdm
from string import punctuation
def remove_punct(string):
    """remvoes leading and trailing punctuation in tokens. This happen due to the different tolenization used when
    recording eye-tracking data.
    e.g. "styles", --> styles """
    string = string.strip(punctuation)
    # special case for geco: remove "...any charactes" e.g. secretary....you
    string = string.split("...")[0]
    string = string.split('."')[0]
    string = string.split(',"')[0]
    string = string.split('!"')[0]

    
    return string
# Set file name
# Download data here: http://expsy.ugent.be/downloads/geco/
geco_original = "dutchgeco.csv"
output_raw = open("dutch_geco2_raw.txt", "w")
output_scaled = open("dutch_geco2_scaled.txt", "w")
tokens = []
feature_names = []
subjects = []
# Read CSV with original gaze data
with open(geco_original) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    header = next(csv_reader, None)
    # select eye-tracking features
    feature_names = [header[12], header[19], header[28], header[46], header[51], header[53], header[56]]
    print("Features:", feature_names)
    for row in tqdm(csv_reader):
        subject = [row[0]]
        # lowercasing all tokens
        word = row[11].lower()
        word = [remove_punct(word)]
        features = [row[12], row[19], row[28], row[46], row[51], row[53], row[56]]
        tokens.append(subject + word + features)
        if subject not in subjects:
            subjects.append(subject)
print("Number of subjects: ", len(subjects))
print("Number of tokens per subject: ", len(tokens)/len(subjects))
print("word", " ".join(feature_names), file=output_raw)
print("word", " ".join(feature_names), file=output_scaled)
types = {}
# Get all word types for each subject
for token in tokens:
    features = []
    for feat in token[2:]:
        # unknown feature values become 0
        if feat == ".":
            feat = 0.0
        else:
            feat = float(feat)
        features.append(feat)
    id = token[0]+"_"+token[1]
    if id not in types:
        types[id] = (features, 1)
    else:
        types[id] = ([x + y for x, y in zip(types[id][0], features)], types[id][1]+1)
# Average the feature values over all word occurrences of 1 subject
avg_types = {}
for x,y in types.items():
    avg_y_subj = [feat / y[1] for feat in y[0]]
    word = x.split("_")[1]
    if word not in avg_types:
        avg_types[word] = avg_y_subj
    else:
        avg_types[word] = [x + y for x,y in zip(avg_types[word], avg_y_subj)]
print("Number of types: ", len(avg_types))
# Average the feature values over all subjects
for x,y in avg_types.items():
    subj_avg = [i/len(subjects) for i in y]
    print(x, " ".join(map(str, subj_avg)), file=output_raw)
    # Scale feature values to range between 0 and 1
    subj_avg_scaled = []
    for idx, feat in enumerate(subj_avg):
        max_value = 0.0
        for feature_list in avg_types.values():
            if feature_list[idx] / len(subjects) > max_value:
                max_value = feature_list[idx] / len(subjects)
        subj_avg_scaled.append(feat / max_value)
    # Check for scaling errors
    if any(t > 1 for t in subj_avg_scaled):
        print("Some scaled values are higher than 1!!!")
        break
    print(x, " ".join(map(str, subj_avg_scaled)), file=output_scaled)