An Overview: Triple-Barrier & Meta-Labeling Techniques

![meta_labeling_architecture.png](meta_labeling_architecture.png)
*note*: this image is from the original text, and is not my own work. also primary model can be adjusted to handle 
    long and short predictions.


The fixed-time horizon technique, a common strategy for labeling data in the world of financial research, isn't without
its flaws. Enter the triple-barrier method—a more dynamic approach that, when paired with meta-labeling, can
significantly boost efficacy.

From the Writings of Marcos Lopez de Prado:

Advances in Financial Machine Learning, Chapter 3
Machine Learning for Asset Managers, Chapter 5
Breaking Down the Triple-Barrier Method:

Three barriers define this method: the upper, the lower, and the vertical. The upper barrier sets the stage for buying
chances (label 1), while the lower barrier defines selling opportunities (label -1). Finally, the vertical barrier
imposes a time limit on observations, with the upper or lower barriers needing to be reached before an observation is labeled 0. Importantly, this method adjusts the upper and lower barriers based on each observation's volatility.

The Essence of Meta-Labeling:

This secondary machine learning model focuses on determining the optimal bet size, without worrying about the side of
the bet (long or short). As the secondary model filters false positives from the primary model, it bolsters overall
accuracy. Key benefits include morphing fundamental models into machine learning models, curbing overfitting,
developing sophisticated strategy structures, and refining decision-making regarding bet sizes.

Putting Meta-Labeling into Practice:

Develop a primary model with high recall, even if precision is low.
Compensate for low precision by applying meta-labeling to the primary model's positive predictions.
By filtering out false positives, meta-labeling enhances the F1-score while the primary model zeroes in on most
positives.
Implementation in Action:

A variety of functions are employed when using the triple-barrier method in tandem with meta-labeling, such as
add_vertical_barrier(), get_events(), get_bins(), and drop_labels(). Comprehensive descriptions of these functions are
available in the original texts.

In a nutshell, the triple-barrier method and meta-labeling work in concert to create a powerful approach to labeling
financial data, remedying the limitations of the fixed-time horizon method. This harmonious collaboration leads to more
precise predictions and more informed decision-making in the realm of financial markets.