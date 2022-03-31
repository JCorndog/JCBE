using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;
using UnityEngine.SceneManagement;

public class ChaserMovement : MonoBehaviour
{
    public bool grounded = false;
    Vector3 speed = new Vector3(0, 0, 0);
    public float xDir = 0;
    float moveSpeedRatio = 0.02f;
    float moveSpeedCap = 0.2f;
    float baseJumpSpeed = 0.3f;
    float footPos = 0;
    float gravity = 0.01f;
    int timer = 30;
    int randDir = 1;
    public BoxCollider2D boxCollider2d;
    public Rigidbody2D rigidbody2D;
    public NNHandler nnInstance;
    public GameObject evader;
    bool left = false;
    bool jump = false;
    bool right = false;

    bool messageReadyToSend = true;
    bool readyToReset = false;
    bool touchedEnemy = false;
    bool touchedWall = false;
    int epoch = 0;
    int step = 0;
    bool randomMove = false;

    public Sprite spriteRandom;
    public SpriteRenderer spriteRenderer;
    public Sprite spriteSmart;

    int[] movement = new int[6]; // [x=0,x>0,x<0,y=0,y>0,y<0]
    EvaderMovement evaderMovement;
    System.Diagnostics.Stopwatch watch = new System.Diagnostics.Stopwatch();

    public bool ready = false;

    void Start()
    {

        Rigidbody2D rigidbody2D = GetComponent<Rigidbody2D>();
        BoxCollider2D boxCollider2d = GetComponent<BoxCollider2D>();
        NNHandler nnInstance = GetComponent<NNHandler>();
        evader = GameObject.Find("Evader");
        evaderMovement = evader.GetComponent<EvaderMovement>();

        SpriteRenderer spriteRenderer = GetComponent<SpriteRenderer>();
        Sprite spriteRandom = GetComponent<Sprite>();
        Sprite spriteSmart = GetComponent<Sprite>();


    }

    void interpretData(byte[] message)
    {
        watch.Stop();
        watch.Restart();
        epoch = BitConverter.ToInt32(message, 0);
        //Debug.Log("Received");
        char flag = (char)message[4];

        if (flag == 'i')
        {
            left = (char)message[5] == '1';
            jump = (char)message[6] == '1';
            right = (char)message[7] == '1';
            if ((char)message[8] == '1')
            {
                randomMove = true;
            }
            else
            {
                randomMove = false;
            }
        }
        else if(flag == 'r')
        {
            // Debug.Log("Ready to reset");
            // Debug.Log(epoch);
            readyToReset = true;
            return;
        }
        else
        {
            // Something else
        }
        messageReadyToSend = true;

    }

    float GetDist2Evader()
    {
        return Vector3.Distance(transform.position, evader.transform.position);
    }

    void update_movement()
    {   // [x=0,x>0,x<0,y=0,y>0,y<0]

        movement[0] = speed.x == 0 ? 1 : 0;
        movement[1] = speed.x > 0 ? 1 : 0;
        movement[2] = speed.x < 0 ? 1 : 0;
        movement[3] = speed.y == 0 ? 1 : 0;
        movement[4] = speed.y > 0 ? 1 : 0;
        movement[5] = speed.y < 0 ? 1 : 0;
    }

    void checkWallTouch()
    {
        //573.5 right
        //554.5 left
        Vector3 vec = transform.position;
        if (vec.x > 572.5 && IsHittingRightWall())
        {
            touchedWall = true;
            Debug.Log("Hit wall");
        }
        else if (vec.x < 555.5 && IsHittingLeftWall())
        {
            touchedWall = true;
            Debug.Log("Hit wall");
        }
        else
        {
            touchedWall = false;
        }
    }


    // Update is called once per frame
    void Update()
    {
        if (!ready)
        {
            return;
        }
        if (randomMove)
        {
            spriteRenderer.sprite = spriteRandom;
        }
        else
        {
            spriteRenderer.sprite = spriteSmart;
        }

        if (readyToReset)
        {
            Debug.Log("Reseting");
            SceneManager.LoadScene(SceneManager.GetActiveScene().name);
            return;
        }
        else
        {
            if (messageReadyToSend)
            {
                checkWallTouch();
                nnInstance.SendData(touchedEnemy, touchedWall, GetDist2Evader(), movement, evaderMovement.movement, interpretData);
                watch.Start();
                //Debug.Log("Sending Message");
                //Debug.Log(step);
                messageReadyToSend = false;
            }
            else if (watch.ElapsedMilliseconds > 300)
            {
                watch.Stop();
                watch.Restart();
                messageReadyToSend = true;
                Debug.Log("Try Again");
            }
        }
        

        xDir = 0;
        //Input
        if (left)
        {
            xDir -= 1;
        }
        if (right)
        {
            xDir += 1;
        }
        if (Math.Abs(speed.x) < moveSpeedCap || Math.Sign(speed.x) != Math.Sign(xDir))
        {
            speed.x += moveSpeedRatio * xDir;
        }
        if (grounded && jump)
        {
            //Debug.Log("jump");
            speed.y = baseJumpSpeed;
            jump = false;
        }
        step++;
        update_movement();
    }

    void FixedUpdate()
    {
        if (!ready)
        {
            return;
        }
        timer--;
        if (timer <= 0)
        {
            randDir = UnityEngine.Random.Range(0, 2);
            timer = UnityEngine.Random.Range(10, 40);
        }
        Vector3 tmp = transform.position;
        grounded = IsGrounded();
        if (!grounded)
        {
            speed.y -= gravity;
        }
        if (grounded && speed.y < 0)
        {
            //Debug.Log("hit ground");
            speed.y = 0;
        }
        if (IsHittingCeiling())
        {
            speed.y = -0.05f;
        }

        /*if (IsHittingLeftWall() || IsHittingRightWall())
        {
            speed.x = 0;
        }*/
        footPos = tmp.y - .5f;
        rigidbody2D.MovePosition(tmp + speed);
        
    }

    public bool IsGrounded()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.down, 0.01f);
        return hit.collider != null;
    }
    public bool IsHittingCeiling()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.up, 0.01f);
        return hit.collider != null;
    }

    public bool IsHittingRightWall()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.right, 0.02f);
        return hit.collider != null;
    }

    public bool IsHittingLeftWall()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.left, 0.02f);
        return hit.collider != null;
    }

    private void OnCollisionEnter2D(Collision2D other)
    {
        if (other.gameObject.tag == "Evader")
        {
            touchedEnemy = true;
        }
    }
}