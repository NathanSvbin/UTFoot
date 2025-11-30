async function loadTeam(teamId) {
    const ul = document.getElementById('players');
    const logo = document.getElementById('clubLogo');

    try {
        const res = await fetch(`../Generateur/get_team.php?id=${teamId}`);
        const data = await res.json();

        // Logo
        if (data?.info?.imageUrl) logo.src = data.info.imageUrl;

        // Joueurs
        ul.innerHTML = '';
        const squad = data?.squad?.squad || [];
        if (squad.length > 0) {
            squad.forEach(p => {
                const li = document.createElement('li');
                li.textContent = `${p.name} - ${p.position ?? ''}`;
                ul.appendChild(li);
            });
        } else {
            ul.innerHTML = '<li>Aucun joueur trouvé</li>';
        }
    } catch (err) {
        ul.innerHTML = '<li>Erreur de chargement API</li>';
        console.error(err);
    }
}
