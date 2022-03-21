using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CreatorScript : MonoBehaviour
{
    public GameObject evader;
    public GameObject chaser;
    // Start is called before the first frame update
    void Start()
    {
        float x_max = 572.5f;
        float x_min = 555.5f;
        float x = Random.Range(x_min, x_max);
        float y = 309.0f;
        Vector3 startpos = new Vector3(x, y, 1.0f);
        evader.transform.position = startpos;
        float x2 = Random.Range(x_min, x_max);
        while (Mathf.Abs(x2 - x) < 3)
        {
            x2 = Random.Range(x_min, x_max);
        }
        startpos = new Vector3(x2, y, 1.0f);
        chaser.transform.position = startpos;
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
