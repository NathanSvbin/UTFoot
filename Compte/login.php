<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

require_once '../Generateur/db_account.php';
session_start();

$errors = [];
$success_html = '';

/* --- Message si l'utilisateur vient de s'inscrire --- */
if (isset($_GET['success'])) {
    $success_html = '<div class="alert alert-success">Inscription réussie, vous pouvez vous connecter.</div>';
}

/* --- Traitement du formulaire --- */
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    $login = trim($_POST['login'] ?? '');
    $password = $_POST['mot_de_passe'] ?? '';

    if ($login === '' || $password === '') {
        $errors[] = "Tous les champs sont obligatoires.";
    } else {
        // IMPORTANT : utiliser $pdo_account (ton fichier db_account.php)
        $stmt = $pdo_account->prepare("SELECT * FROM users WHERE email = ? OR username = ? LIMIT 1");
        $stmt->execute([$login, $login]);

        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$user) {
            $errors[] = "Identifiants incorrects.";
        } else {
            // Vérification du mot de passe avec la bonne colonne ('password')
            if (!password_verify($password, $user['mot_de_passe'])) {
                $errors[] = "Identifiants incorrects.";
            } else {
                // Connexion réussie
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['username'] = $user['username'];
                $_SESSION['email'] = $user['email'];

                header("Location: compte.php");
                exit;
            }
        }
    }
}

/* --- Affichage des erreurs --- */
$errors_html = '';
if (!empty($errors)) {
    $errors_html .= '<div class="alert alert-danger">';
    foreach ($errors as $e) {
        $errors_html .= '<p>' . htmlspecialchars($e) . '</p>';
    }
    $errors_html .= '</div>';
}
?>


<!DOCTYPE html>
<html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" type="text/css" href="../assets/CSS/style.css">
        <title>Connexion - FootIQ</title>
    </head>

    <body>
        <nav class="navbar navbar-expand-lg">
            <div class="container-fluid">
                <a class="navbar-brand" href="../index.html">
                    <img class="logo" src="../assets/IMG/Logo.png" alt="Logo" width="100" height="100">
                </a>
            </div>
        </nav>

        <div id="box" class="container mt-5 d-flex justify-content-center">
            <div class="w-100" style="max-width:600px;">
                <h2 class="mb-4 text-center">Connexion</h2>

                <?= $success_html ?>
                <?= $errors_html ?>

                <form method="POST" action="login.php">
                    <div class="mb-3">
                        <label class="form-label">Email ou Nom d'utilisateur</label>
                        <input type="text" class="form-control" name="login" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Mot de passe</label>
                        <input type="password" class="form-control" name="mot_de_passe" required>
                    </div>

                    <button type="submit" class="btn btn-primary w-100">Se connecter</button>
                </form>

                <p class="mt-3 text-center">
                    Pas encore de compte ? <a href="register.php">Créer un compte</a>
                </p>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
    </body>
</html>
