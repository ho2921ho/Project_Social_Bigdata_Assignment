# 사용자함수



from sklearn.cluster import AgglomerativeClustering
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.manifold import TSNE ; tsne = TSNE(random_state=42)
from sklearn.decomposition import PCA ; pca = PCA(n_components = 2)
from sklearn.metrics import silhouette_samples, silhouette_score
import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 1000000
mpl.rcParams.update({'figure.max_open_warning': 0})

def FindKsil(X_scaled,mink,maxk):
    X_tsne = tsne.fit_transform(X_scaled)
    cluster_range = range(mink,maxk)
    for n_clusters in cluster_range:
      fig, (ax1, ax2) = plt.subplots(1, 2) # Create a subplot with 1 row and 2 columns
      fig.set_size_inches(18, 7)
      ax1.set_xlim([-1, 1]) # The 1st subplot is the silhouette plot
      ax1.set_ylim([0, len(X_scaled) + (n_clusters + 1) * 10]) # The (n_clusters+1)*10 is for inserting blank space between silhouette # plots of individual clusters, to demarcate them clearly.
      clusterer = AgglomerativeClustering(n_clusters=n_clusters)  # Initialize the clusterer with n_clusters value and a random generator # seed of 10 for reproducibility.
      cluster_labels = clusterer.fit_predict( X_scaled )
      # clusters
      silhouette_avg = silhouette_score(X_scaled, cluster_labels) # The silhouette_score gives the average value for all the samples.  # This gives a perspective into the density and separation of the formed
      print("For n_clusters =", n_clusters,
            "The average silhouette_score is :", silhouette_avg)
    
      # Compute the silhouette scores for each sample
      sample_silhouette_values = silhouette_samples(X_scaled, cluster_labels)
    
      y_lower = 10
      for i in range(n_clusters):
          # Aggregate the silhouette scores for samples belonging to
          # cluster i, and sort them
          ith_cluster_silhouette_values = \
              sample_silhouette_values[cluster_labels == i]
    
          ith_cluster_silhouette_values.sort()
    
          size_cluster_i = ith_cluster_silhouette_values.shape[0]
          y_upper = y_lower + size_cluster_i
    
          color = cm.nipy_spectral(float(i)/n_clusters)
          ax1.fill_betweenx(np.arange(y_lower, y_upper),
                            0, ith_cluster_silhouette_values,
                            facecolor=color, edgecolor=color, alpha=0.7)
    
          # Label the silhouette plots with their cluster numbers at the middle
          ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
    
          # Compute the new y_lower for next plot
          y_lower = y_upper + 10  # 10 for the 0 samples
    
      ax1.set_title("The silhouette plot for the various clusters.")
      ax1.set_xlabel("The silhouette coefficient values")
      ax1.set_ylabel("Cluster label")
    
      # The vertical line for average silhoutte score of all the values
      ax1.axvline(x=silhouette_avg, color="red", linestyle="--")
    
      ax1.set_yticks([])  # Clear the yaxis labels / ticks
      ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
    
      # 2nd Plot showing the actual clusters formed
      colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
      ax2.scatter(X_tsne[:,0],X_tsne[:,1], marker='.', s=30, lw=0, alpha=0.7,
                  c=colors)
    
      ax2.set_title("The visualization of the clustered data.")
      ax2.set_xlabel("Feature space for the 1st coordinate")
      ax2.set_ylabel("Feature space for the 2nd coordinate")
    
      plt.suptitle(("Silhouette analysis for Agglomerative clustering on sample data "
                    "with n_clusters = %d" % n_clusters),
                   fontsize=14, fontweight='bold')
    
      plt.show() 