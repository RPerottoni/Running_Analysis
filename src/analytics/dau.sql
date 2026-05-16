-- DAU: Stands for "Daily Active Users"

SELECT substr(DtCriacao,0, 11) as DtDia,
       COUNT(DISTINCT IdCliente) as DAU
FROM transacoes
GROUP BY 1
ORDER BY DtDia