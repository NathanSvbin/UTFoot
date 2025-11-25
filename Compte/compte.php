<?php
session_start();

// Vérifie si un utilisateur est connecté
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}

$nom = $_SESSION['username']; // correspond à ce que tu stockes dans login.php
?>

<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="../assets/CSS/style.css">
    <title>Bienvenue</title>
</head>

<body>
    <nav class="navbar navbar-expand-lg">
        <div class="container-fluid">
            <a class="navbar-brand" href="../index.html">
                <img class="logo" src="../assets/IMG/Logo.png" alt="Logo" width="100" height="100">
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item"><a class="nav-link" href="../index.html">Accueil</a></li>
                    <li class="nav-item"><a class="nav-link" href="../Match/match.hmtl">Match</a></li>
                    <li class="nav-item"><a class="nav-link active" href="championnat.html">Championnat</a></li>
                    <li class="nav-item"><a class="nav-link" href="../Classement/classment.html">Classement</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">Mon Compte</a></li>
                </ul>

                <form class="d-flex" role="search" method="GET" action="../php/recherche.php">
                    <input class="form-control me-2" type="search" placeholder="Recherche" name="query">
                    <button class="btn btn-outline-success" type="submit">Recherche</button>
                </form>
            </div>
        </div>
    </nav>

    <!-- ─────────── BOX AVEC MESSAGE DE BIENVENUE ─────────── -->
    <div id="box" class="container mt-5">
        <div class="alert alert-primary text-center p-4 fs-4">
            👋 Bonjour <strong><?php echo htmlspecialchars($nom); ?></strong> !
            <br>Ravi de vous revoir.
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>