<?php
include('db.php');

if (!isset($_GET['q']) || trim($_GET['q']) === '') {
    die("Aucune recherche spécifiée.");
}

$q = "%" . $_GET['q'] . "%";

$stmt = $conn->prepare("
    SELECT 
        ch.Id AS id_championnat,
        ch.Nom AS nom_championnat,
        p.Nom AS nom_pays,
        co.Nom AS nom_continent
    FROM Championnat ch
    JOIN Pays p ON ch.Id_Pays = p.Id
    JOIN Continent co ON p.Id_Continent = co.Id
    WHERE ch.Nom LIKE ?
       OR p.Nom LIKE ?
       OR co.Nom LIKE ?
    ORDER BY ch.Nom ASC
");

$stmt->bind_param('sss', $q, $q, $q);
$stmt->execute();
$res = $stmt->get_result();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Résultats de recherche</title>
</head>
<body>

<h1>Résultats pour "<?php echo htmlspecialchars($_GET['q']); ?>"</h1>

<?php if ($res->num_rows === 0) { ?>

    <p>Aucun championnat trouvé.</p>

<?php } else { ?>

    <table border="1" cellpadding="10">
        <tr>
            <th>Championnat</th>
            <th>Pays</th>
            <th>Continent</th>
        </tr>

        <?php while ($row = $res->fetch_assoc()) { ?>
        <tr>
            <td>
                <a href="championnat.php?id=<?php echo intval($row['id_championnat']); ?>">
                    <?php echo htmlspecialchars($row['nom_championnat']); ?>
                </a>
            </td>
            <td><?php echo htmlspecialchars($row['nom_pays']); ?></td>
            <td><?php echo htmlspecialchars($row['nom_continent']); ?></td>
        </tr>
        <?php } ?>

    </table>

<?php } ?>

<p><a href="championnat.html">← Retour à la liste des championnats</a></p>

</body>
</html>
