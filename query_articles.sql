use rss_feeds;



SELECT 
categories.category, 
url,
title,
summary,
date_published,
CONVERT(embeddings.summary_vector USING utf8) as summary_vectors,
CONVERT(embeddings.category_vector USING utf8) as category_vector
 from metadata 
left join summary on metadata.summary_id = summary.id
left join embeddings on embeddings.summary_id = summary.id
left join categories on embeddings.category_vector = categories.category_vector
WHERE date_published > DATE_ADD(now(),interval -2 day);  --   where summary LIKE '%XML%'

Select * from metadata;