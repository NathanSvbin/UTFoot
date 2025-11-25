<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

require_once '../Generateur/db_account.php';


// variables pour afficher les erreurs / valeurs persistantes
$errors = [];
$old = [
    'firstname' => '',
    'lastname' => '',
    'username' => '',
    'email' => ''
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $old['firstname'] = trim($_POST['firstname'] ?? '');
    $old['lastname']  = trim($_POST['lastname'] ?? '');
    $old['username']  = trim($_POST['username'] ?? '');
    $old['email']     = trim($_POST['email'] ?? '');
    $password         = $_POST['password'] ?? '';
    $password_repeat  = $_POST['password_repeat'] ?? '';

    // validations
    if ($old['firstname'] === '' || $old['lastname'] === '' || $old['username'] === '' || $old['email'] === '' || $password === '') {
        $errors[] = "Tous les champs sont obligatoires.";
    }

    if (!filter_var($old['email'], FILTER_VALIDATE_EMAIL)) {
        $errors[] = "Email invalide.";
    }

    if ($password !== $password_repeat) {
        $errors[] = "Les mots de passe ne correspondent pas.";
    }

    if (empty($errors)) {
        // vérifier si l'email ou le username existe déjà
        $stmt = $pdo->prepare("SELECT id FROM users WHERE email = ? OR username = ?");
        $stmt->execute([$old['email'], $old['username']]);
        if ($stmt->rowCount() > 0) {
            $errors[] = "Un utilisateur avec cet email ou ce nom d'utilisateur existe déjà.";
        } else {
            $hashed = password_hash($password, PASSWORD_DEFAULT);

            $insert = $pdo->prepare("
                INSERT INTO users (nom, prenom, username, email, mot_de_passe, date_creation)
                VALUES (?, ?, ?, ?, ?, NOW())
            ");
            // attention : dans ta table tu utilises nom/prenom ; ici on met lastname -> nom, firstname -> prenom
            $insert->execute([$old['lastname'], $old['firstname'], $old['username'], $old['email'], $hashed]);

            header("Location: login.php?success=1");
            exit;
        }
    }
}

// préparation HTML des erreurs
$errors_html = '';
if (!empty($errors)) {
    $errors_html .= '<div class="alert alert-danger"><ul>';
    foreach ($errors as $e) {
        $errors_html .= '<li>' . htmlspecialchars($e) . '</li>';
    }
    $errors_html .= '</ul></div>';
}
?>
<!DOCTYPE html>
<html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
        <link rel="stylesheet" type="text/css" href="../assets/CSS/style.css">
        <title>Inscription - FootIQ</title>
    </head>

    <body>
        <nav class="navbar navbar-expand-lg">
            <div class="container-fluid">
                <a class="navbar-brand" href="../index.html">
                    <img class="logo" src="../assets/IMG/Logo.png" alt="Logo" width="100" height="100">
                </a>
                <!-- tu peux garder le reste de la nav si besoin -->
            </div>
        </nav>

        <div id="box" class="container mt-5 d-flex justify-content-center">
            <div class="w-100" style="max-width:600px;">
                <h2 class="mb-4 text-center">Créer un compte</h2>

                <?= $errors_html ?>

                <form method="POST" action="register.php">
                    <div class="row mb-3">
                        <div class="col">
                            <input type="text" class="form-control" name="firstname" placeholder="Prénom" required value="<?= htmlspecialchars($old['firstname']) ?>">
                        </div>
                        <div class="col">
                            <input type="text" class="form-control" name="lastname" placeholder="Nom" required value="<?= htmlspecialchars($old['lastname']) ?>">
                        </div>
                    </div>

                    <div class="input-group mb-3">
                        <span class="input-group-text">@</span>
                        <input type="text" class="form-control" name="username" placeholder="Nom d'utilisateur" required value="<?= htmlspecialchars($old['username']) ?>">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Adresse email</label>
                        <input type="email" class="form-control" name="email" required value="<?= htmlspecialchars($old['email']) ?>">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Mot de passe</label>
                        <input type="password" class="form-control" name="password" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Répéter le mot de passe</label>
                        <input type="password" class="form-control" name="password_repeat" required>
                    </div>

                    <button type="submit" class="btn btn-primary w-100">S'inscrire</button>
                </form>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous"></script>
    </body>
</html>
