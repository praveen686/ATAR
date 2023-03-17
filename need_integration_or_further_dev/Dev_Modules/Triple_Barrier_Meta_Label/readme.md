Triple-Barrier and Meta-Labeling: Simplified Explanation

![meta_labeling_architecture.png](meta_labeling_architecture.png)
*note*: this image is from the original text, and is not my own work. also primary model can be adjusted to handle 
    long and short predictions.

The fixed-time horizon method is a widely-used labeling technique in financial academia. However, it has several
shortcomings, which are addressed by the triple-barrier method. The triple-barrier method can also be combined with
meta-labeling to further enhance its effectiveness.

Sources:

Advances in Financial Machine Learning, Chapter 3 by Marcos Lopez de Prado
Machine Learning for Asset Managers, Chapter 5 by Marcos Lopez de Prado

Triple-Barrier Method:

The triple-barrier method involves three barriers: an upper, a lower, and a vertical barrier. The upper barrier
represents the return threshold for buying opportunities (label 1), the lower barrier represents the return threshold
for selling opportunities (label -1), and the vertical barrier represents the time limit for an observation to reach
either the upper or lower barrier before being labeled 0. This method dynamically adjusts the upper and lower barriers
based on the volatility of each observation.

Meta-Labeling:

Meta-labeling is a secondary machine learning (ML) model that helps determine the appropriate bet size without deciding
the side (long or short) of the bet. The secondary ML model filters false positives from the primary model, increasing
overall accuracy. It has several advantages, including transforming fundamental models into ML models, limiting
overfitting effects, enabling sophisticated strategy structures, and improving decision-making for bet sizing.

How to Use Meta-Labeling:

Build a primary model with high recall, even if the precision is low.
Correct for low precision by applying meta-labeling to the positive predictions of the primary model.
Meta-labeling will improve the F1-score by filtering out false positives, while the primary model identifies most
positives.
Implementation:

Several functions are used for the triple-barrier method in conjunction with meta-labeling. These functions include
add_vertical_barrier(), get_events(), get_bins(), and drop_labels(). Detailed descriptions of these functions can be
found in the original text.

In summary, the triple-barrier method and meta-labeling provide a robust approach to labeling financial data by
addressing the shortcomings of the fixed-time horizon method. The combination of these techniques results in more
accurate predictions and improved decision-making in financial markets.