<?php
include('../db.php');  // adapte le chemin selon ton dossier

$sql = "
    SELECT 
        ch.Id AS id_championnat,
        ch.Nom AS nom_championnat,
        p.Nom AS nom_pays,
        co.Nom AS nom_continent
    FROM Championnat ch
    JOIN Pays p ON ch.Id_Pays = p.Id
    JOIN Continent co ON p.Id_Continent = co.Id
";

$result = $conn->query($sql);

?>

<table>
    <tr>
        <th>Championnat</th>
        <th>Pays</th>
        <th>Continent</th>
    </tr>

    <?php while ($row = $result->fetch_assoc()) { ?>
    <tr>
        <td><?= htmlspecialchars($row['nom_championnat']) ?></td>
        <td><?= htmlspecialchars($row['nom_pays']) ?></td>
        <td><?= htmlspecialchars($row['nom_continent']) ?></td>
    </tr>
    <?php } ?>
</table>
