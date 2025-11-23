SELECT
    a.au_fname,
    a.au_lname,
    SUM(s.qty) AS total_ventas
FROM
    authors AS a
JOIN
    titleauthor AS ta ON a.au_id = ta.au_id
JOIN
    titles AS t ON ta.title_id = t.title_id
JOIN
    sales AS s ON t.title_id = s.title_id
GROUP BY
    a.au_fname,
    a.au_lname
ORDER BY
    total_ventas ASC;