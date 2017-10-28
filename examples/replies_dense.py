#%%
import mailscanner
replies = mailscanner.datasets.LabeledTextFileDataset('./replies.txt')

#%%
# one hot encode the labels
from sklearn.preprocessing import LabelEncoder, LabelBinarizer, OneHotEncoder
from sklearn.pipeline import Pipeline
label_encoder = LabelEncoder()
onehot_encoder = Pipeline([
    ('binarizer', LabelBinarizer()),
    ('onehot', OneHotEncoder())
])
labels = label_encoder.fit_transform(replies.labels)
# mildly tricky, need to wrap the array in an array
targets = onehot_encoder.fit_transform(labels).toarray()
targets.shape

#%%
# take a peek at a few one hot labels
targets[0:10]

#%%
# now set up sequencing and embedding
from vectoria import CharacterTrigramEmbedding
trigram = CharacterTrigramEmbedding()
sources = trigram.sequencer.transform(replies.texts)
sources.shape

#%%
# take a peek at some ngram sequences
sources[0:10]

#%%
# data is loaded and preprocesed, now create a keras model to encode
# Here is a very simple -- dense -- model,
# not taking into any real consideration the structure of text,
# or the sequential nature of words or ngrams.
import keras
inputs = keras.layers.Input(shape=(trigram.maxlen,))
embedded = trigram.model(inputs)
stack = keras.layers.Dense(128, activation='relu')(embedded)
stack = keras.layers.Dropout(0.5)(stack)
stack = keras.layers.Dense(128, activation='relu')(stack)
stack = keras.layers.Dropout(0.5)(stack)
# softmax on two classes -- which map to our 0, 1 one hots
flattened = keras.layers.Flatten()(stack)
outputs = keras.layers.Dense(2, activation='softmax')(flattened)
model = keras.models.Model(inputs=inputs, outputs=outputs)
model.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)
model.summary()
model.fit(
    x=sources,
    y=targets, 
    validation_split=0.05,
    batch_size=32,
    epochs=32
)
