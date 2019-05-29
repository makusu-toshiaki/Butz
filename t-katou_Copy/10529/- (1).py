fig, axs = plt.subplots(ncols=5, figsize=(20,15))
axs = axs.flatten()
for i, t in enumerate(range(lda.num_topics)):
    x = dict(lda.show_topic(t, 30))
    im = WordCloud(
        font_path=fpath,
        background_color='white',
        random_state=0
    ).generate_from_frequencies(x)
    axs[i].imshow(im)
    axs[i].axis('off')
    axs[i].set_title('Topic '+str(t))
        
plt.tight_layout()
plt.show()