using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;
using UnityEngine.SceneManagement;

public class CreatorScript : MonoBehaviour
{
    public GameObject evader;
    public GameObject chaser;
    public CompositeCollider2D walls;
    public Collider2D evaderCollider;
    public Collider2D chaserCollider;

    ContactFilter2D contactFilter = new ContactFilter2D();
    Collider2D[] results = new Collider2D[100];

    public bool spawnedEvader = false;
    public bool spawnedChaser = false;


    void spawn_evader()
    {
        float x_max = 573.4f;
        float x_min = 554.6f;
        float y_min = 308.7f;
        float y_max = 312.7f;
        float x = UnityEngine.Random.Range(x_min, x_max);
        float y = UnityEngine.Random.Range(y_min, y_max);
        Vector3 startpos = new Vector3(x, y, 1.0f);
        evader.transform.position = startpos;
    }

    bool evader_valid()
    {
        return evaderCollider.OverlapCollider(contactFilter, results) < 2;
    }

    void spawn_chaser()
    {
        float x_max = 573.4f;
        float x_min = 554.6f;
        float y_min = 308.7f;
        float y_max = 312.7f;
        float x = UnityEngine.Random.Range(x_min, x_max);
        float y = UnityEngine.Random.Range(y_min, y_max);
        Vector3 startpos = new Vector3(x, y, 1.0f);
        int trys = 0;
        while (Mathf.Abs(x - evader.transform.position.x) < 3)
        {
            x = UnityEngine.Random.Range(x_min, x_max);
            if (trys>1000)
            {
                throw new Exception("Can't find spot for chaser.");
            }
            trys++;
        }
        startpos = new Vector3(x, y, 1.0f);
        chaser.transform.position = startpos;
    }

    bool chaser_valid()
    {
        return chaserCollider.OverlapCollider(contactFilter, results) < 1;
    }

    // Start is called before the first frame update
    void Start()
    {
        Physics.autoSimulation = false;
        Scene scene = SceneManager.GetActiveScene();
        if (scene.name == "Challenge1")
        {
            float x_max = 573.4f;
            float x_min = 554.6f;
            float x = UnityEngine.Random.Range(x_min, x_max);
            float y = 308.7f;
            Vector3 startpos = new Vector3(x, y, 1.0f);
            evader.transform.position = startpos;
            float x2 = UnityEngine.Random.Range(x_min, x_max);
            while (Mathf.Abs(x2 - x) < 3)
            {
                x2 = UnityEngine.Random.Range(x_min, x_max);
            }
            startpos = new Vector3(x2, y, 1.0f);
            chaser.transform.position = startpos;
        }
        else if (scene.name == "Challenge2")
        {
            spawn_evader();
            spawn_chaser();
        }
        else if (scene.name == "Challenge3")
        {
            spawn_evader();
            spawn_chaser();
        }
        else
        {

        }
        
    }

    void FixedUpdate()
    {
        if (!spawnedEvader)
        {
            if (evader_valid())
            {
                spawnedEvader = true;
                (evader.GetComponent(typeof(EvaderMovement)) as EvaderMovement).ready = true;
            }
            else
            {
                spawn_evader();
            }
        }
        else if (!spawnedChaser)
        {
            if (chaser_valid())
            {
                spawnedChaser = true;
                (chaser.GetComponent(typeof(ChaserMovement)) as ChaserMovement).ready = true;
            }
            else
            {
                spawn_chaser();
            }
        }
        else
        {
            Physics.Simulate(Time.fixedDeltaTime);
        }
        
    }

    


    // Update is called once per frame
    void Update()
    {
        
    }
}
