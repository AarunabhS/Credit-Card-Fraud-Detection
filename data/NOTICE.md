# Dataset attribution and licence notice

This sample is derived from the Credit Card Fraud Detection database collected by
Worldline and the Machine Learning Group at Université Libre de Bruxelles (ULB),
distributed by the authors through [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud).
The download mirror is linked by [TensorFlow's official tutorial](https://www.tensorflow.org/tutorials/structured_data/imbalanced_data).

The source database is offered under the [Open Database Licence 1.0](https://opendatacommons.org/licenses/odbl/1-0/),
and the contents under the [Database Contents Licence 1.0](https://opendatacommons.org/licenses/dbcl/1-0/).
This derived sample database is offered under those same terms. Credit the source and
retain this notice and the database licence when redistributing the sample.
Changes: exact duplicate rows removed, then a stratified 50,000-row sample selected with seed 42;
rows sorted by transaction Time. PCA features retain their original meanings and labels.
