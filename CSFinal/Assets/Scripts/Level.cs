using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class Level : MonoBehaviour
{
    public int level;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void gotoLevel()
    {
        string levelName = "Level" + level.ToString();
        Debug.Log(levelName);
        SceneManager.LoadScene(sceneName: levelName);
        SceneManager.UnloadSceneAsync(sceneName: "LevelSelect");
    }
}
