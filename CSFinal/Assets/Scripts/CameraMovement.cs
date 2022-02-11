using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraMovement : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }
    public Transform player;
    public Vector3 offset;
    float xTo = 0;
    float yTo = 0;

    // Update is called once per frame
    void Update()
    {
        if(player != null)
        {
            xTo = player.position.x - transform.position.x;
            yTo = player.position.y - transform.position.y;
            transform.position = new Vector3(transform.position.x + xTo / 200, transform.position.y + yTo / 200, 0); // Camera follows the player with specified offset position
        }
    }
}
