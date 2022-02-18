using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenu : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void PlayGame() 
    {
        SceneManager.LoadScene(sceneName:"LevelSelect");
        SceneManager.UnloadSceneAsync(sceneName: "Main Menu");
    }

    public void gotoInstructions()
    {
        SceneManager.LoadScene(sceneName:"Instructions");
        SceneManager.UnloadSceneAsync(sceneName: "Main Menu");
    }

    public void QuitGame()
    {
        Debug.Log("QUIT!");
        Application.Quit();
    }
}
