import requests
import streamlit as st
from typing import Optional, Dict, List
from dataclasses import dataclass

# Configurações da API
BASE_URL = "https://api.github.com"

@dataclass
class GitHubRepo:
	"""Classe para armazenar dados do repositório."""
	name: str
	description: Optional[str]
	language: Optional[str]
	stars: int
	forks: int
	url: str

@dataclass
class GitHubUser:
	"""Classe para armazenar dados do usuário do GitHub."""
	login: str
	avatar_url: str
	bio: str
	url: str
	name: Optional[str]
	public_repos: int
	followers: int
	following: int
	location: Optional[str]
	created_at: str
	repositories: List[GitHubRepo]

class GitHubAPI:
	"""Classe para gerenciar as chamadas à API do GitHub."""
	
	@staticmethod
	def buscar_repositorios(username: str) -> List[GitHubRepo]:
		"""Busca os repositórios do usuário."""
		try:
			response = requests.get(f'{BASE_URL}/users/{username}/repos')
			response.raise_for_status()
			repos_data = response.json()
			return [
				GitHubRepo(
					name=repo['name'],
					description=repo.get('description'),
					language=repo.get('language'),
					stars=repo['stargazers_count'],
					forks=repo['forks_count'],
					url=repo['html_url']
				)
				for repo in repos_data
			]
		except requests.exceptions.RequestException:
			return []

	@staticmethod
	def buscar_usuario(username: str) -> Optional[GitHubUser]:
		"""
		Busca informações de um usuário no GitHub.
		
		Args:
			username (str): Nome de usuário do GitHub
			
		Returns:
			Optional[GitHubUser]: Objeto com dados do usuário ou None se não encontrado
		"""
		try:
			response = requests.get(f'{BASE_URL}/users/{username}')
			response.raise_for_status()
			data = response.json()
			
			# Busca os repositórios do usuário
			repositories = GitHubAPI.buscar_repositorios(username)
			
			return GitHubUser(
				login=data['login'],
				avatar_url=data['avatar_url'],
				bio=data.get('bio', 'Biografia não disponível'),
				url=data['html_url'],
				name=data.get('name'),
				public_repos=data['public_repos'],
				followers=data['followers'],
				following=data['following'],
				location=data.get('location'),
				created_at=data['created_at'].split('T')[0],
				repositories=repositories
			)
		except requests.exceptions.RequestException:
			return None

class Interface:
	"""Classe para gerenciar a interface do usuário."""
	
	@staticmethod
	def configurar_pagina():
		"""Configura o estilo e aparência da página."""
		st.set_page_config(
			page_title="Consulta GitHub",
			page_icon="👨‍💻",
			layout="wide"
		)
		st.markdown('''
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.6/dist/css/bootstrap.min.css" 
				  rel="stylesheet">
			<style>
				.card {
					margin: 20px auto;
					box-shadow: 0 4px 8px rgba(0,0,0,0.1);
				}
				.user-stats {
					display: flex;
					justify-content: space-around;
					margin: 10px 0;
				}
				.repo-card {
					border: 1px solid #e1e4e8;
					border-radius: 6px;
					padding: 16px;
					margin: 8px 0;
				}
				.repo-card:hover {
					background-color: #f6f8fa;
				}
				.search-container {
					display: flex;
					align-items: center;
					gap: 10px;
				}
				.language-tag {
					display: inline-block;
					padding: 3px 8px;
					border-radius: 12px;
					font-size: 12px;
					background-color: #e1e4e8;
					margin-right: 8px;
				}
			</style>
		''', unsafe_allow_html=True)

	def exibir_repositorios(self, repos: List[GitHubRepo]):
		"""Exibe a lista de repositórios do usuário."""
		st.markdown("### 📚 Repositórios")
		
		for repo in repos:
			st.markdown(f'''
				<div class="repo-card">
					<h4>
						<a href="{repo.url}" target="_blank" style="text-decoration: none;">
							📁 {repo.name}
						</a>
					</h4>
					<p>{repo.description or "Sem descrição"}</p>
					<div>
						{f'<span class="language-tag">{repo.language}</span>' if repo.language else ''}
						⭐ {repo.stars} stars
						🔄 {repo.forks} forks
					</div>
				</div>
			''', unsafe_allow_html=True)

	def exibir_perfil(self, usuario: GitHubUser):
		"""
		Exibe o perfil do usuário na interface.
		
		Args:
			usuario (GitHubUser): Objeto com dados do usuário
		"""
		col1, col2 = st.columns([1, 2])
		
		with col1:
			st.markdown(f'''
				<div class="card">
					<img src="{usuario.avatar_url}" class="card-img-top" alt="Avatar do usuário">
					<div class="card-body">
						<h3 class="card-title">{usuario.name or usuario.login}</h3>
						<h6 class="text-muted">@{usuario.login}</h6>
						<p class="card-text">{usuario.bio}</p>
						
						<div class="user-stats">
							<div class="text-center">
								<strong>{usuario.public_repos}</strong>
								<div>Repositórios</div>
							</div>
							<div class="text-center">
								<strong>{usuario.followers}</strong>
								<div>Seguidores</div>
							</div>
							<div class="text-center">
								<strong>{usuario.following}</strong>
								<div>Seguindo</div>
							</div>
						</div>
						
						<p class="mt-3">
							<i class="bi bi-geo-alt"></i> {usuario.location or 'Localização não informada'}
						</p>
						<p>
							<i class="bi bi-calendar"></i> Membro desde {usuario.created_at}
						</p>
						<a href="{usuario.url}" class="btn btn-primary w-100" target="_blank">
							Ver perfil no GitHub
						</a>
					</div>
				</div>
			''', unsafe_allow_html=True)
		
		with col2:
			self.exibir_repositorios(usuario.repositories)

def main():
	"""Função principal do aplicativo."""
	interface = Interface()
	interface.configurar_pagina()
	
	st.title("🔍 Consulta GitHub")
	st.write("Digite um nome de usuário do GitHub para ver suas informações.")
	
	# Container de busca com layout melhorado
	with st.container():
		col1, col2, col3 = st.columns([3, 1, 3])
		with col1:
			username = st.text_input("", placeholder="Digite o username")
		with col2:
			buscar = st.button('🔎 Buscar', use_container_width=True)
		with col3:
			st.write("")  # Espaço em branco para alinhamento
	
	if buscar and username:
		with st.spinner('Buscando informações...'):
			github_api = GitHubAPI()
			usuario = github_api.buscar_usuario(username)
			
			if usuario:
				interface.exibir_perfil(usuario)
			else:
				st.error("❌ Usuário não encontrado ou erro na consulta.")

if __name__ == "__main__":
	main()


	
	
	
	
