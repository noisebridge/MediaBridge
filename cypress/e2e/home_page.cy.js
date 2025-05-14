describe('The Home Page', () => {
    it('successfully loads', () => {
      cy.visit('/')
    })
  })

describe('Movie Search using fixture', () => {

  beforeEach(() => {
    // Intercept the search API and return fixture data
    cy.intercept('GET', '/api/v1/movie/search*', { fixture: 'movies.json' }).as('movieSearch');
  });

  it('should display movies from fixture', () => {
    cy.visit('/')

    cy.get('input[name="movie-search"]').type('Inception{enter}');

    cy.wait('@movieSearch');

    cy.contains('Inception').should('exist');
  });

//   it('should correctly handle searches with no matches', () => {
//     // You can dynamically adjust the intercepted response
//     cy.intercept('GET', '/api/v1/movie/search*', []).as('emptySearch');

//     cy.visit('http://localhost:5000');
    
//     cy.get('input[name="search"]').type('NonExistentMovie{enter}');

//     cy.wait('@emptySearch');

//     cy.contains('No movies found').should('exist');
//   });
});