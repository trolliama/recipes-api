# Recipes API
A pretty basic recipe API project made in djangoREST Framework for learning

## Endpoints
> Base url - 127.0.0.1:8000

- #### POST
  - **Create a new user**
    > /api/user/create
    
    ```json
    {
      "email": "example@email.com",
      "password": "examplepassword",
      "name": "example"
    }
    ```
  - **Create/Get user token**
    > /api/user/token
    
    ```json
    {
      "email": "example@email.com",
      "password": "examplepassword"
    }
    ```
  - **Create new tags**
    > /api/recipes/tags
    
    ```json
    {
      "name": "tag name"
    }
    ```
  - **Create new ingredients**
    > /api/recipes/ingredients
    
    ```json
    {
      "name": "ingredient name"
    }
    ```
  - **Create new recipes**
    > /api/recipes/recipe
    
    ```json
    {
      "title": "RecipeTitleExample",
      "time_minutes": 12,
      "price": 12.5,
      "ingredients": [1,2],
      "tags": [3],
      "link": ""
    }
    ```
  
