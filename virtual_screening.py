# -*- coding: utf-8 -*-
"""Virtual screening.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1S3hYtxrjm7cXR0wuZI4uuAdINSk2_Jmj
"""

!pip install rdkit

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import IPythonConsole
import pandas as pd
from rdkit.Chem import PandasTools
from rdkit.Chem import Descriptors
from rdkit.Chem import rdmolops
import seaborn as sns

# Loading the dataset
active_df = pd.read_csv("/content/actives_final.ism",header=None,sep= " ")
active_rows,active_cols = active_df.shape
active_df.columns = ["SMILES","ID","ChEMBL_ID"]
active_df["label"] = ["Active"]*active_rows
PandasTools.AddMoleculeColumnToFrame(active_df,"SMILES","Mol")

# Def a function to compute certain parameters of the molecules
# These properties encode the size of a molecule, its ability to partition from
# an oily substance (octanol) to water, and whether the molecule has a positive or negative charge.
def add_property_columns_to_df(df_in):
  df_in["mw"] = [Descriptors.MolWt(mol) for mol in df_in.Mol]
  df_in["logP"] = [Descriptors.MolLogP(mol) for mol in df_in.Mol]
  df_in["charge"] = [rdmolops.GetFormalCharge(mol) for mol in df_in.Mol]

add_property_columns_to_df(active_df)

active_df.head()

# let's apply the previous code to the decoy molecules
decoy_df = pd.read_csv("/content/decoys_final.ism",header=None,sep=" ")
decoy_df.columns = ["SMILES","ID"]
decoy_rows, decoy_cols = decoy_df.shape
decoy_df["label"] = ["Decoy"]*decoy_rows
PandasTools.AddMoleculeColumnToFrame(decoy_df,"SMILES","Mol")
add_property_columns_to_df(decoy_df)

# Creating a new df
tmp_df = pd.concat([active_df, decoy_df])

# Comparison of the properties
sns.violinplot(x="label", y="mw", data=tmp_df)
plt.show()

"""The previous plots shows a roughly similar distributions but the central MW (middle box) are very similar

"""

sns.violinplot(x="label", y="logP", data=tmp_df)
plt.show()

sns.violinplot(x="label", y="charge", data=tmp_df)
plt.show()

# Since there are evident differences between the charge of the decoy molecules, we want to know that fraction
charged = decoy_df[decoy_df["charge"] != 0]
charged.shape[0]/decoy_df.shape[0]
# The result is the fraction of charged molecules

import pandas as pd
from rdkit import Chem
from rdkit.Chem import PandasTools
import seaborn as sns
import matplotlib.pyplot as plt

# Definition of a function to neutralize the charged molecules
def neutralize_molecules(df):
    for idx, row in df.iterrows():
        mol = Chem.MolFromSmiles(row["SMILES"])
        total_charge = Chem.GetFormalCharge(mol)
        if total_charge != 0:
            num_hydrogens = abs(total_charge)
            if total_charge > 0:
                for _ in range(num_hydrogens):
                    mol = Chem.AddHs(mol)
            elif total_charge < 0:
                for _ in range(num_hydrogens):
                    mol = Chem.RemoveHs(mol)
        df.at[idx, "Mol"] = mol
    return df

# Reading decoy cvs
decoy_df = pd.read_csv("/content/decoys_final.ism", header=None, sep=" ")
decoy_df.columns = ["SMILES", "ID"]
decoy_df["label"] = ["Decoy"] * decoy_df.shape[0]

# Neutralizing the loaded molecules in the decoy df
decoy_df = neutralize_molecules(decoy_df)

# New df creation to work with
revised_decoy_df = decoy_df[["SMILES", "ID", "label"]].copy()

# Violin plot generated to compare charge distributions
sns.violinplot(x=revised_decoy_df["label"], y=revised_decoy_df["charge"])
plt.xlabel("Label")
plt.ylabel("Charge")
plt.title("Distribution of Charges in Neutralized Decoy Molecules")
plt.show()

# Model creation: GraphConv model (classification)
# To have a model to be reusable, save it in an accesible directory
def generate_graph_conv_model():
batch_size = 128
model = GraphConvModel(1, batch_size=batch_size, mode='classification', model_dir="/tmp/mk01/model_dir")
return model

# Load and split the data in training and test dataset
dataset_file = "dude_erk2_mk01.CSV"
tasks = ["is_active"]
featurizer = dc.feat.ConvMolFeaturizer()
loader = dc.data.CSVLoader(tasks=tasks,
smiles_field="SMILES",
    featurizer=featurizer)
dataset = loader.featurize(dataset_file, shard_size=8192)
splitter = dc.splits.RandomSplitter()

# The dataset is unbalanced because there are more inactive than active compounds
# the metric to be used is Matthews correlation
 metrics = [
    dc.metrics.Metric(dc.metrics.matthews_corrcoef, np.mean,
    mode="classification")]

# Model performance
 training_score_list = []
    validation_score_list = []
    transformers = []
    cv_folds = 10
for i in range(0, cv_folds):
model = generate_graph_conv_model()
res = splitter.train_valid_test_split(dataset) train_dataset, valid_dataset, test_dataset = res model.fit(train_dataset)
train_scores = model.evaluate(train_dataset, metrics, transformers)
training_score_list.append( train_scores["mean-matthews_corrcoef"]) validation_scores = model.evaluate(valid_dataset, metrics,
transformers)
validation_score_list.append( validation_scores["mean-matthews_corrcoef"]) print(training_score_list) print(validation_score_list)

# To visualize the performance of the models in both training and test dataset
ns.boxplot(
    ["training"] * cv_folds + ["validation"] * cv_folds,
    training_score_list + validation_score_list)

# Visualization the model results
pred = [x.flatten() for x in model.predict(valid_dataset)]
pred_df = pd.DataFrame(pred,columns=["neg","pos"])
pred_df["active"] = [int(x) for x in valid_dataset.y]
pred_df["SMILES"] = valid_dataset.ids

# Boxplots (to compare predicted values for active and inactive)
 sns.boxplot(pred_df.active,pred_df.pos)

#checking the false positives and negatives and creation a df containing only the active molecules with a positive score < 0.5
false_negative_df = pred_df.query("active == 1 & pos < 0.5").copy()

#Inspecting chemical structures
PandasTools.AddMoleculeColumnToFrame(false_negative_df,
    "SMILES", "Mol")

# The training of the model was on the training dataset
# The validation on the test dataset
# To evaluate the performance we will train the model on all data
model.fit(dataset)
model.save()

"""Preparing dataset for model **prediction**"""

# Import necessary libraries
import pandas as pd
from collections import Counter
from rdkit import Chem
from rdkit.Chem import Draw

# Run the rd_filters.py script to filter problematic molecules
# This should be executed in the command line, not in Python
# rd_filters.py filter --in zinc_100k.smi --prefix zinc

# Read the output file generated by rd_filters.py
df = pd.read_csv("zinc.CSV")
print(df.head())

# Count the number of molecules rejected by each filter
count_list = list(Counter(df.FILTER).items())
count_df = pd.DataFrame(count_list, columns=["Rule", "Count"])
count_df.sort_values("Count", inplace=True, ascending=False)
print(count_df.head())

# Generate an image highlighting 1,2-dicarbonyl functional groups
smiles_list = df[df['FILTER'] == 'Filter41_12_dicarbonyl']['SMILES'].tolist()
mol_list = [Chem.MolFromSmiles(x) for x in smiles_list]
dicarbonyl = Chem.MolFromSmarts('*C(=O)C(=O)*')
match_list = [mol.GetSubstructMatch(dicarbonyl) for mol in mol_list]

# Create an image with the highlighted molecules
img = Draw.MolsToGridImage(mol_list, highlightAtomLists=match_list, molsPerRow=5)
img.show()

"""Applying the predictive model

"""

# Import necessary libraries
import deepchem as dc
import pandas as pd
from rdkit.Chem import PandasTools, Draw
from rdkit import DataStructs
from rdkit.ML.Cluster import Butina
from rdkit.Chem import rdMolDescriptors as rdmd
import seaborn as sns

# Load the predictive model
model = dc.models.TensorGraph.load_from_dir("/tmp/mk01/model_dir")

# Create a featurizer to read the to-analyzed chemical structures and convert them into numbers to feed the model
featurizer = dc.feat.ConvMolFeaturizer()

# Read and prepare the input SMILES file
df = pd.read_csv("zinc.smi", sep=" ", header=None)
df.columns = ["SMILES", "Name"]
df["Val"] = [0] * len(df)

# Save the dataframe to a CSV file for DeepChem input
infile_name = "zinc_filtered.csv"
df.to_csv(infile_name, index=False)

# Use DeepChem to read the CSV file and featurize the molecules
loader = dc.data.CSVLoader(tasks=['Val'], smiles_field="SMILES", featurizer=featurizer)
dataset = loader.featurize(infile_name, shard_size=8192)

# Generate predictions with the model
pred = model.predict(dataset)

# Put the predictions into a Pandas dataframe (getting scores of certain activities or properties)
pred_df = pd.DataFrame([x.flatten() for x in pred], columns=["Neg", "Pos"])

# Combine the predictions with the original data
combo_df = df.join(pred_df, how="outer")
combo_df.sort_values("Pos", inplace=True, ascending=False)

# Visualize the distribution of the scores
sns.histplot(combo_df['Pos'], kde=True)

# Display the chemical structures of the top predicted molecules
PandasTools.AddMoleculeColumnToFrame(combo_df, smilesCol='SMILES')
Draw.MolsToGridImage(combo_df.Mol[:10], molsPerRow=5, legends=["%.2f" % x for x in combo_df.Pos[:10]])

# Define a function for Butina clustering
# The clustering is necessary in order to keep representative samples
def butina_cluster(mol_list, cutoff=0.35):
    fp_list = [rdmd.GetMorganFingerprintAsBitVect(m, 3, nBits=2048) for m in mol_list]
    dists = []
    nfps = len(fp_list)
    for i in range(1, nfps):
        sims = DataStructs.BulkTanimotoSimilarity(fp_list[i], fp_list[:i])
        dists.extend([1 - x for x in sims])
    mol_clusters = Butina.ClusterData(dists, nfps, cutoff, isDistData=True)
    cluster_id_list = [0] * nfps
    for idx, cluster in enumerate(mol_clusters, 1):
        for member in cluster:
            cluster_id_list[member] = idx
    return cluster_id_list

# Select the top 100 scoring molecules
best_100_df = combo_df.head(100).copy()

# Cluster the selected molecules
best_100_df["Cluster"] = butina_cluster(best_100_df.Mol)
print(best_100_df.head())

# Determine the number of unique clusters
print("Number of unique clusters:", len(best_100_df.Cluster.unique()))

# Select one representative molecule per cluster
best_cluster_rep_df = best_100_df.drop_duplicates("Cluster")
print("Shape of the clustered dataframe:", best_cluster_rep_df.shape)

# Save the selected molecules to a CSV file
best_cluster_rep_df.to_csv("best_cluster_representatives.csv", index=False)