async function loadTeam(teamId) {
    const playersUl = document.getElementById('players');
    const clubLogo = document.getElementById('clubLogo');

    try {
        const res = await fetch(`https://ton-serveur.com/api/get_team.php?id=${teamId}`);
        const data = await res.json();

        // Logo
        if (data?.info?.imageUrl) clubLogo.src = data.info.imageUrl;

        // Joueurs
        playersUl.innerHTML = '';
        const squad = data?.squad?.squad || [];
        if (squad.length > 0) {
            squad.forEach(p => {
                const li = document.createElement('li');
                li.textContent = `${p.name} - ${p.position ?? ''}`;
                playersUl.appendChild(li);
            });
        } else {
            playersUl.innerHTML = '<li>Aucun joueur trouvé</li>';
        }

    } catch (err) {
        playersUl.innerHTML = '<li>Erreur de chargement API</li>';
        console.error(err);
    }
}
